import telebot

from settings.logger_conf import logger_configure
from controller.logic_layer import *
from settings.settings import BOT_TOKEN
from tools.add_admins_tool import init_admins
from tools.add_tags_tool import init_tags

init_admins()
init_tags()
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
ll = LogicLayer(bot)
logger_configure()
logger = logging.getLogger("article_tgbot")


@bot.message_handler(commands=['help'])
def help_command(message):
    chat_id = message.chat.id
    ll.help_hint(chat_id)


@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    ll.start_cmd(chat_id)


@bot.message_handler(commands=['student_number'])
def university_id_command(message):
    chat_id = message.chat.id
    ll.student_number_cmd(chat_id)


@bot.message_handler(commands=['tags'])
def tags_command(message):
    chat_id = message.chat.id
    ll.tags_cmd(chat_id)


@bot.message_handler(commands=['text'])
def create_or_replace_article_text(message):
    text = message.text[6:]
    chat_id = message.chat.id
    ll.create_or_edit_article(chat_id, text, message.id)


@bot.message_handler(content_types=['photo'])
def create_or_replace_article_with_img(message):
    text = message.caption
    img_id = message.photo[0].file_id
    chat_id = message.chat.id
    ll.create_or_edit_article(chat_id, text, img_id, message.id)


@bot.callback_query_handler(func=lambda call: not ll.is_admin_lambda(call))
def handle_keyboard(call):
    chat_id = call.message.chat.id
    text = call.data
    message_id = call.message.id
    ll.handle_keyboard(chat_id, text, message_id)


@bot.callback_query_handler(func=lambda call: ll.is_admin_lambda(call))
def handle_admin_keyboard(call):
    chat_id = call.message.chat.id
    text = call.data
    message_id = call.message.id
    ll.handle_admin_keyboard(chat_id, text, message_id)


bot.polling(none_stop=True, interval=0)
