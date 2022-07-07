import telebot
import re
from keyboa import Keyboa

from bot_data_layer import *


bot = telebot.TeleBot(TOKEN_STUDENT, parse_mode=None)
con_pool = get_con_pool()


@bot.message_handler(commands=['help'])
def help_command(message):
    chat_id = message.chat.id
    con = con_pool.getconn()
    if is_user_admin(chat_id, con):
        bot.send_message(message.chat.id,
                         "Загрузити изображение с текстом для формирования статьи или просто текст,"
                         " после чего выберите теги для статьи (не менее одног) и нажмите 'опубликовать'"
                         "Новый текст и фото будут обновлять вашу статью, если она не опубликована")
    else:
        bot.send_message(chat_id,
                         "Для начала работы введите номер студенческого билета с помощью команды /student_number "
                         "Для изменения списка выбранных тэгов введите команду /tags и выберите желаемые тэги")
    con_pool.putconn(con)


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


@bot.message_handler(commands=['text'])
def create_or_replace_article_text(message):
    text = message.text
    text = text[6:]
    print(text)
    chat_id = message.chat.id
    con = con_pool.getconn()
    if is_user_admin(chat_id, con):
        set_text_and_img_to_article(chat_id, text, "", con)
        bot.send_message(chat_id=chat_id,
                         text="Данные внесены успешно")
        set_admin_categories_markup(chat_id)
    else:
        bot.send_message(chat_id=chat_id,
                         text="Вы не являетесь администратором")
    con_pool.putconn(con)


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
        con = con_pool.getconn()
        set_university_id(chat_id, stud_number, con)
        con_pool.putconn(con)
        return True
    else:
        bot.send_message(chat_id, "Введен неправильный формат номера. Формат m******* или без m")
        return False


@bot.callback_query_handler(func=lambda call: not is_user_admin_lambda(call))
def handle_keyboard(call):
    text = call.data
    message_id = call.message.id
    chat_id = call.message.chat.id
    con = con_pool.getconn()
    if text == "Найти":
        handle_find_btn(chat_id, message_id, con)
    elif text in categories:
        handle_category_btn(chat_id, message_id, text, con)
    elif text == "Назад":
        handle_back_btn(chat_id, message_id)
    else:
        handle_tag_btn(chat_id, message_id, text, con)
    con_pool.putconn(con)


@bot.callback_query_handler(func=lambda call: is_user_admin_lambda(call))
def handle_admin_keyboard(call):
    chat_id = call.message.chat.id
    text = call.data
    message_id = call.message.id
    con = con_pool.getconn()
    if text == "Опубликовать":
        handle_post_btn(chat_id, message_id, con)
    elif text in categories:
        handle_admin_category_btn(chat_id, message_id, text, con)
    elif text == "Назад":
        handle_admin_back_btn(chat_id, message_id)
    else:
        handle_admin_tag_btn(chat_id, message_id, text, con)
    con_pool.putconn(con)


@bot.message_handler(content_types=['photo'])
def create_or_replace_article_with_img(message):
    text = message.caption
    img_id = message.photo[0].file_id
    chat_id = message.chat.id
    con = con_pool.getconn()
    if is_user_admin(chat_id, con):
        set_text_and_img_to_article(chat_id, text, img_id, con)
        bot.send_message(chat_id=chat_id,
                         text="Данные внесены успешно")
        set_admin_categories_markup(chat_id)
    else:
        bot.send_message(chat_id=chat_id,
                         text="Вы не являетесь администратором")
    con_pool.putconn(con)


def handle_find_btn(chat_id, message_id, connection):
    print("Конец настройки")
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
        print(articles)
        for article in articles:
            if article[1]:
                print(article)
                bot.send_photo(chat_id=chat_id,
                               caption=article[0],
                               photo=article[1])
            else:
                bot.send_message(chat_id=chat_id,
                                 text=article[0])


def handle_category_btn(chat_id, message_id, category_name, connection):
    print("Категория")
    markup = create_tags_markup(category_name, chat_id, connection)
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=category_name,
                          reply_markup=markup)


def handle_back_btn(chat_id, message_id):
    print("Назад")
    markup = create_categories_markup()
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text="Выберите нужные теги и нажмите найти",
                          reply_markup=markup)


def handle_tag_btn(chat_id, message_id, tag_name, connection):
    print("Теги")
    emoji_index = tag_name.find(" ✅")
    if emoji_index != -1:
        tag_name = tag_name[:emoji_index]
    print(tag_name)
    set_tag_to_student(chat_id, tag_name, connection)
    category = get_category_by_tag(tag_name, connection)
    markup = create_tags_markup(category, chat_id, connection)
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=category,
                          reply_markup=markup)


def handle_post_btn(chat_id, message_id, connection):
    print("Публикация")
    article = post_article(chat_id, connection)
    if article:
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text="Успешная публикация")
        article_id = article[0]
        article_text = article[1]
        article_img = article[2]
        print(article_id)
        approp_students = get_approp_students(article_id, connection)
        print(approp_students)
        if article_img:
            for student in approp_students:
                bot.send_photo(chat_id=student[0],
                               caption=article_text,
                               photo=article_img)
        else:
            for student in approp_students:
                bot.send_message(chat_id=student[0],
                                 text=article_text)
    else:
        bot.send_message(chat_id=chat_id,
                         text="У статьи нет тегов")


def handle_admin_category_btn(chat_id, message_id, category_name, connection):
    print("Категория")
    article_id = get_article_id(chat_id, connection)
    markup = create_admin_tags_markup(category_name, article_id, connection)
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=category_name,
                          reply_markup=markup)


def handle_admin_back_btn(chat_id, message_id):
    print("Назад")
    markup = create_admin_categories_markup()
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text="Выберите нужные теги и нажмите опубликовать",
                          reply_markup=markup)


def handle_admin_tag_btn(chat_id, message_id, tag_name, connection):
    print("Теги")
    emoji_index = tag_name.find(" ✅")
    if emoji_index != -1:
        tag_name = tag_name[:emoji_index]
    print(tag_name)
    article_id = get_article_id(chat_id, connection)
    print(article_id)
    set_tag_to_article(article_id, tag_name, connection)
    category = get_category_by_tag(tag_name, connection)
    markup = create_admin_tags_markup(category, article_id, connection)
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=category,
                          reply_markup=markup)


def create_categories_markup():
    return Keyboa(items=list(categories), copy_text_to_callback=True).keyboard


def create_tags_markup(category, chat_id, connection):
    print(category)
    index = categories.index(category)
    items = list(tags[index])
    marked_tags = get_marked_tags(category, chat_id, connection)
    print(f"marked_tags '{marked_tags}'")
    for i in range(len(items) - 1):
        print(items[i])
        if items[i] in marked_tags:
            items[i] = items[i] + " ✅"
    return Keyboa(items=items).keyboard


def create_admin_tags_markup(category, article_id, connection):
    print(category)
    index = categories_admin.index(category)
    items = list(tags_admin[index])
    marked_tags = get_admin_marked_tags(category, article_id, connection)
    print(f"marked_tags '{marked_tags}'")
    for i in range(len(items) - 1):
        print(items[i])
        if items[i] in marked_tags:
            items[i] = items[i] + " ✅"
    return Keyboa(items=items).keyboard


def set_admin_categories_markup(chat_id):
    markup = create_admin_categories_markup()
    bot.send_message(chat_id=chat_id,
                     text="Выберите нужные теги и нажмите опубликовать",
                     reply_markup=markup)


def create_admin_categories_markup():
    return Keyboa(items=list(categories_admin), copy_text_to_callback=True).keyboard


bot.polling()
