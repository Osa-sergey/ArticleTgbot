import telebot

from bot_data_layer import DataLayer
from bot_logic_layer import *
from settings import TOKEN_STUDENT

bot = telebot.TeleBot(TOKEN_STUDENT, parse_mode=None)
dl = DataLayer()
ll = LogicLayer(bot, dl)


@bot.message_handler(commands=['help'])
def help_command(message):
    chat_id = message.chat.id
    if dl.is_user_admin(chat_id):
        bot.send_message(message.chat.id,
                         "Загрузити изображение с текстом для формирования статьи или просто текст,"
                         " после чего выберите теги для статьи (не менее одног) и нажмите 'опубликовать'"
                         "Новый текст и фото будут обновлять вашу статью, если она не опубликована")
    else:
        bot.send_message(chat_id,
                         "Для начала работы введите номер студенческого билета с помощью команды /student_number "
                         "Для изменения списка выбранных тэгов введите команду /tags и выберите желаемые тэги")


@bot.message_handler(commands=['start'])
def start_command(message):
    msg = bot.send_message(message.chat.id, "Введите номер студенческого билета")
    bot.register_next_step_handler(msg, ll.init_university_id_and_tags)


@bot.message_handler(commands=['student_number'])
def university_id_command(message):
    msg = bot.send_message(message.chat.id, "Введите номер студенческого билета")
    bot.register_next_step_handler(msg, ll.save_university_id)


@bot.message_handler(commands=['tags'])
def tags_command(message):
    chat_id = message.chat.id
    markup = ll.create_categories_markup(dl.is_user_admin(chat_id))
    bot.send_message(message.chat.id,
                     "Выберите нужные теги и нажмите найти",
                     reply_markup=markup)


@bot.message_handler(commands=['text'])
def create_or_replace_article_text(message):
    text = message.text
    text = text[6:]
    print(text)
    chat_id = message.chat.id
    if dl.is_user_admin(chat_id):
        dl.set_text_and_img_to_article(chat_id, text, "")
        bot.send_message(chat_id=chat_id,
                         text="Данные внесены успешно")
        ll.set_admin_categories_markup(chat_id)
    else:
        bot.send_message(chat_id=chat_id,
                         text="Вы не являетесь администратором")


@bot.callback_query_handler(func=lambda call: not dl.is_user_admin_lambda(call))
def handle_keyboard(call):
    text = call.data
    message_id = call.message.id
    chat_id = call.message.chat.id
    if text == "Найти":
        ll.handle_find_btn(chat_id, message_id)
    elif text in categories:
        ll.handle_category_btn(chat_id, message_id, text)
    elif text == "Назад":
        ll.handle_back_btn(chat_id, message_id)
    else:
        ll.handle_tag_btn(chat_id, message_id, text)


@bot.callback_query_handler(func=lambda call: dl.is_user_admin_lambda(call))
def handle_admin_keyboard(call):
    chat_id = call.message.chat.id
    text = call.data
    message_id = call.message.id
    if text == "Опубликовать":
        ll.handle_post_btn(chat_id, message_id)
    elif text in categories:
        ll.handle_admin_category_btn(chat_id, message_id, text)
    elif text == "Назад":
        ll.handle_admin_back_btn(chat_id, message_id)
    else:
        ll.handle_admin_tag_btn(chat_id, message_id, text)


@bot.message_handler(content_types=['photo'])
def create_or_replace_article_with_img(message):
    text = message.caption
    img_id = message.photo[0].file_id
    chat_id = message.chat.id
    if dl.is_user_admin(chat_id):
        dl.set_text_and_img_to_article(chat_id, text, img_id)
        bot.send_message(chat_id=chat_id,
                         text="Данные внесены успешно")
        ll.set_admin_categories_markup(chat_id)
    else:
        bot.send_message(chat_id=chat_id,
                         text="Вы не являетесь администратором")


bot.polling(none_stop=True, interval=0)
