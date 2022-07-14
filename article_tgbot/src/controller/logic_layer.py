import logging
import re

from article_tgbot.src.controller.service.admin.admin_keyboard_handler_service import AdminKeyHandlerService
from article_tgbot.src.controller.service.admin.admin_markup_service import AdminMarkupService
from article_tgbot.src.controller.service.admin_service import is_admin
from article_tgbot.src.controller.service.student.keyboard_handler_service import KeyHandlerService
from article_tgbot.src.controller.service.student.markup_service import MarkupService
from article_tgbot.src.model.data_layer import DataLayer
from article_tgbot.src.tags import *
from article_tgbot.settings.text_settings import *


class LogicLayer:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(LogicLayer, cls).__new__(cls)
        return cls.__instance

    def __init__(self, bot):
        self.bot = bot
        self.dl = DataLayer()
        self.akh = AdminKeyHandlerService(bot)
        self.kh = KeyHandlerService(bot)
        self.logger = logging.getLogger(__name__)

    def init_university_id_and_tags(self, message):
        if not self.save_university_id(message):
            return
        self.tags_command(message)

    def tags_command(self, message):
        chat_id = message.chat.id
        markup = self.create_categories_markup(chat_id)
        self.bot.send_message(chat_id, tags_choose_and_search, reply_markup=markup)

    def save_university_id(self, message):
        number = message.text
        chat_id = message.chat.id
        pattern = r'^[m]{0,1}[0-9]{7}$'
        res = re.search(pattern, number)
        if res is not None:
            self.bot.send_message(chat_id, student_number_accepted)
            stud_number = res.group(0)
            if len(stud_number) == 8:
                stud_number = stud_number[1:]
            self.dl.set_university_id(chat_id, stud_number)
            return True
        else:
            self.bot.send_message(chat_id, student_number_format_error)
            return False

    def set_admin_categories_markup(self, chat_id):
        markup = self.create_categories_markup(chat_id)
        self.bot.send_message(chat_id=chat_id,
                              text=tags_choose_and_publish,
                              reply_markup=markup)

    @staticmethod
    def is_admin_lambda(call):
        return is_admin(call.message.chat.id)

    def set_article(self, chat_id, text, img_id):
        self.dl.set_text_and_img_to_article(chat_id, text, img_id)

    def create_or_edit_article(self, chat_id, text, img_id=""):
        if is_admin(chat_id):
            self.set_article(chat_id, text, img_id)
            self.bot.send_message(chat_id=chat_id, text=data_accepted)
            self.set_admin_categories_markup(chat_id)
        else:
            self.bot.send_message(chat_id=chat_id, text=not_admin)

    def handle_keyboard(self, chat_id, text, message_id):
        if text == find:
            self.kh.handle_find_btn(chat_id, message_id)
        elif text in categories:
            self.kh.handle_category_btn(chat_id, message_id, text)
        elif text == back:
            self.kh.handle_back_btn(chat_id, message_id)
        else:
            self.kh.handle_tag_btn(chat_id, message_id, text)

    def handle_admin_keyboard(self, chat_id, text, message_id):
        if text == publish:
            self.akh.handle_post_btn(chat_id, message_id)
        elif text in categories:
            self.akh.handle_admin_category_btn(chat_id, message_id, text)
        elif text == back:
            self.akh.handle_admin_back_btn(chat_id, message_id)
        else:
            self.akh.handle_admin_tag_btn(chat_id, message_id, text)

    @staticmethod
    def create_categories_markup(chat_id):
        if is_admin(chat_id):
            return AdminMarkupService.create_categories_markup()
        else:
            return MarkupService.create_categories_markup()

    def help_hint(self, chat_id):
        if is_admin(chat_id):
            self.bot.send_message(chat_id, help_admin)
        else:
            self.bot.send_message(chat_id, help_student)
