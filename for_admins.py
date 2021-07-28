import telebot
from telebot import types
from keyboa import Keyboa
from tools import *

bot = telebot.TeleBot(TOKEN_ADMIN, parse_mode=None)
student_bot = telebot.TeleBot(TOKEN_STUDENT, parse_mode=None)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id,
                     "Загрузити изображение с текстом для формирования статьи или просто текст,"
                     " после чего выберите теги для статьи (не менее одног) и нажмите 'опубликовать'"
                     "Новый текст и фото будут обновлять вашу статью, если она не опубликована")


@bot.callback_query_handler(func=lambda call: True)
def handle_keyboard(call):
    text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.id
    connection = create_connection(db_name, db_user, db_password, db_host, db_port)
    if text == "Опубликовать":
        handle_post_btn(chat_id, message_id, connection)
    elif text in categories:
        handle_category_btn(chat_id, message_id, text, connection)
    elif text == "Назад":
        handle_back_btn(chat_id, message_id)
    else:
        handle_tag_btn(chat_id, message_id, text, connection)
    connection.close()


def handle_post_btn(chat_id, message_id, connection):
    article = post_article(chat_id, connection)
    if article:
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text="Успешная публикация")
        article_id = article[0]
        article_text = article[1]
        article_img = article[2]
        approp_students = get_approp_students(article_id, connection)
        if article_img:
            for student in approp_students:
                student_bot.send_photo(chat_id=student[0],
                                       caption=article_text,
                                       photo=article_img)
        else:
            for student in approp_students:
                student_bot.send_message(chat_id=student[0],
                                         text=article_text)
    else:
        bot.send_message(chat_id=chat_id,
                         text="У статьи нет тегов")


def post_article(chat_id, connection):
    res = execute_query_with_result(connection,
                                    post_article_query,
                                    (chat_id,))
    return res[0]


def get_approp_students(article_id, connection):
    return execute_query_with_result(connection,
                                     get_students_for_article_query,
                                     (article_id,))


def handle_category_btn(chat_id, message_id, category_name, connection):
    article_id = get_article_id(chat_id, connection)
    markup = create_tags_markup(category_name, article_id, connection)
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=category_name,
                          reply_markup=markup)


def handle_back_btn(chat_id, message_id):
    markup = create_categories_markup()
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text="Выберите нужные теги и нажмите опубликовать",
                          reply_markup=markup)


def handle_tag_btn(chat_id, message_id, tag_name, connection):
    emoji_index = tag_name.find(" ✅")
    if emoji_index != -1:
        tag_name = tag_name[:emoji_index]
    article_id = get_article_id(chat_id, connection)
    set_tag_to_article(article_id, tag_name, connection)
    category = get_category_by_tag(tag_name, connection)
    markup = create_tags_markup(category, article_id, connection)
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=category,
                          reply_markup=markup)


def get_article_id(chat_id, connection):
    res = execute_query_with_result(connection,
                                    get_article_id_query,
                                    (chat_id,))
    return res[0][0]


def set_tag_to_article(article_id, tag_name, connection):
    execute_query(connection,
                  set_tag_to_article_query,
                  (article_id, tag_name))


def create_tags_markup(category, article_id, connection):
    index = categories_admin.index(category)
    items = list(tags_admin[index])
    marked_tags = get_marked_tags(category, article_id, connection)
    for i in range(len(items) - 1):
        if items[i] in marked_tags:
            items[i] = items[i] + " ✅"
    return Keyboa(items=items).keyboard


def get_marked_tags(category, article_id, connection):
    res = execute_query_with_result(connection,
                                    get_article_marked_tags_query,
                                    (article_id, category))
    if res:
        return res[0]
    else:
        return []


@bot.message_handler(content_types=['photo'])
def create_or_replace_article_with_img(message):
    text = message.caption
    img_id = message.photo[0].file_id
    chat_id = message.chat.id
    connection = create_connection(db_name, db_user, db_password, db_host, db_port)
    if can_user_use_bot(chat_id, connection):
        set_text_and_img_to_article(chat_id, text, img_id, connection)
        bot.send_message(chat_id=chat_id,
                         text="Данные внесены успешно")
        set_categories_markup(chat_id)
    else:
        bot.send_message(chat_id=chat_id,
                         text="Вы не являетесь администратором")
    connection.close()


@bot.message_handler()
def create_or_replace_article_text(message):
    text = message.text
    chat_id = message.chat.id
    connection = create_connection(db_name, db_user, db_password, db_host, db_port)
    if can_user_use_bot(chat_id, connection):
        set_text_and_img_to_article(chat_id, text, "", connection)
        bot.send_message(chat_id=chat_id,
                         text="Данные внесены успешно")
        set_categories_markup(chat_id)
    else:
        bot.send_message(chat_id=chat_id,
                         text="Вы не являетесь администратором")
    connection.close()


def can_user_use_bot(chat_id, connection):
    res = execute_query_with_result(connection,
                                    has_admin_permissions_query,
                                    (chat_id,))
    if res:
        return True
    else:
        return False


def set_text_and_img_to_article(chat_id, text, img_id, connection):
    execute_query(connection,
                  set_text_and_img_to_article_query,
                  (chat_id, text, img_id))


def set_categories_markup(chat_id):
    markup = create_categories_markup()
    bot.send_message(chat_id=chat_id,
                     text="Выберите нужные теги и нажмите опубликовать",
                     reply_markup=markup)


def create_categories_markup():
    return Keyboa(items=list(categories_admin), copy_text_to_callback=True).keyboard


bot.polling()
