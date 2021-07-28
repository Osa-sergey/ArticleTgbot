import telebot
import re
from telebot import types
from keyboa import Keyboa
from tools import *

bot = telebot.TeleBot(TOKEN_STUDENT, parse_mode=None)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id,
                     "Для начала работы введите номер студенческого билета с помощью команды /student_number "
                     "Для изменения списка выбранных тэгов введите команду /tags и выберите желаемые тэги")


@bot.message_handler(commands=['start'])
def start_command(message):
    msg = bot.send_message(message.chat.id, "Введите номер студенческого билета")
    bot.register_next_step_handler(msg, init_university_id_and_tags)


@bot.message_handler(commands=['student_number'])
def university_id_command(message):
    msg = bot.send_message(message.chat.id, "Введите номер студенческого билета")
    bot.register_next_step_handler(msg, save_university_id)


@bot.message_handler(commands=['tags'])
def tags_command(message):
    markup = create_categories_markup()
    bot.send_message(message.chat.id,
                     "Выберите нужные теги и нажмите найти",
                     reply_markup=markup)


def init_university_id_and_tags(message):
    if not save_university_id(message):
        return
    tags_command(message)


def save_university_id(message):
    number = message.text
    chat_id = message.chat.id
    pattern = r'^[m]{0,1}[0-9]{7}$'
    res = re.search(pattern, number)
    if res is not None:
        bot.send_message(chat_id, "Номер удачно внесен")
        stud_number = res.group(0)
        if len(stud_number) == 8:
            stud_number = stud_number[1:]
        connection = create_connection(db_name, db_user, db_password, db_host, db_port)
        set_university_id(chat_id, stud_number, connection)
        return True
    else:
        bot.send_message(chat_id, "Введен неправильный формат номера. Формат m******* или без m")
        return False


@bot.callback_query_handler(func=lambda call: True)
def handle_keyboard(call):
    text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.id
    connection = create_connection(db_name, db_user, db_password, db_host, db_port)
    if text == "Найти":
        handle_find_btn(chat_id, message_id, connection)
    elif text in categories:
        handle_category_btn(chat_id, message_id, text, connection)
    elif text == "Назад":
        handle_back_btn(chat_id, message_id)
    else:
        handle_tag_btn(chat_id, message_id, text, connection)
    connection.close()


def handle_find_btn(chat_id, message_id, connection):
    if not has_user_university_id(chat_id, connection):
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text="Вы не ввели номер студенческого билета. Воспользуйтесь /student_number или /start")
    elif not has_marked_tags(chat_id, connection):
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text="Выберите хотя бы один тег")
    else:
        articles = get_articles(chat_id, connection)
        for article in articles:
            if article[1]:
                bot.send_photo(chat_id=chat_id,
                               caption=article[0],
                               photo=article[1])
            else:
                bot.send_message(chat_id=chat_id,
                                 text=article[0])


def handle_category_btn(chat_id, message_id, category_name, connection):
    markup = create_tags_markup(category_name, chat_id, connection)
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=category_name,
                          reply_markup=markup)


def handle_back_btn(chat_id, message_id):
    markup = create_categories_markup()
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text="Выберите нужные теги и нажмите найти",
                          reply_markup=markup)


def handle_tag_btn(chat_id, message_id, tag_name, connection):
    emoji_index = tag_name.find(" ✅")
    if emoji_index != -1:
        tag_name = tag_name[:emoji_index]
    set_tag_to_student(chat_id, tag_name, connection)
    category = get_category_by_tag(tag_name, connection)
    markup = create_tags_markup(category, chat_id, connection)
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=category,
                          reply_markup=markup)


def create_categories_markup():
    return Keyboa(items=list(categories), copy_text_to_callback=True).keyboard


def create_tags_markup(category, chat_id, connection):
    index = categories.index(category)
    items = list(tags[index])
    marked_tags = get_marked_tags(category, chat_id, connection)
    for i in range(len(items) - 1):
        if items[i] in marked_tags:
            items[i] = items[i] + " ✅"
    return Keyboa(items=items).keyboard


def has_user_university_id(chat_id, connection):
    result = execute_query_with_result(connection,
                                       has_university_id_query,
                                       (chat_id,))
    if result:
        return True
    else:
        return False


def has_marked_tags(chat_id, connection):
    result = execute_query_with_result(connection,
                                       has_marked_tags_query,
                                       (chat_id,))
    if result:
        return True
    else:
        return False


def get_articles(chat_id, connection):
    return execute_query_with_result(connection,
                                     get_articles_query,
                                     (chat_id,))


def get_marked_tags(category, chat_id, connection):
    res = execute_query_with_result(connection,
                                    get_student_marked_tags_query,
                                    (chat_id, category))
    if res:
        return res[0]
    else:
        return []


def set_university_id(chat_id, stud_number, connection):
    execute_query(connection,
                  update_university_id_query,
                  (chat_id, stud_number, stud_number))


def set_tag_to_student(chat_id, tag_name, connection):
    execute_query(connection,
                  set_tag_to_student_query,
                  (chat_id, tag_name))


bot.polling()
