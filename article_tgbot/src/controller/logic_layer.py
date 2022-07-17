import logging
import re

from article_tgbot.src.controller.service.admin.admin_keyboard_handler_service import AdminKeyHandlerService
from article_tgbot.src.controller.service.admin.admin_markup_service import AdminMarkupService
from article_tgbot.src.controller.service.admin_service import is_admin
from article_tgbot.src.controller.service.student.keyboard_handler_service import KeyHandlerService
from article_tgbot.src.controller.service.student.markup_service import MarkupService
from article_tgbot.src.model.data_layer import DataLayer
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
        self.ams = AdminMarkupService()
        self.ms = MarkupService()
        self.logger = logging.getLogger(__name__)

    def init_university_id_and_tags(self, message):
        if not self.save_university_id(message):
            return
        self.logger.info("Successful registration", extra={"user": message.chat.id})
        self.tags_command(message)

    def tags_command(self, message):
        chat_id = message.chat.id
        markup = self.create_categories_markup(chat_id)
        self.bot.send_message(chat_id, tags_choose_and_search, reply_markup=markup)

    def save_university_id(self, message):
        number = message.text
        chat_id = message.chat.id
        self.logger.debug("Number for check matching student number format", extra={"user": chat_id, "number": number})
        pattern = r'^[m]{0,1}[0-9]{7}$'
        res = re.search(pattern, number)
        if res is not None:
            stud_number = res.group(0)
            self.logger.debug("Matched student number", extra={"user": chat_id, "student_number": stud_number})
            if len(stud_number) == 8:
                stud_number = stud_number[1:]
            self.dl.set_university_id(chat_id, stud_number)
            self.logger.info("Successful saving of the student number", extra={"user": chat_id})
            self.bot.send_message(chat_id, student_number_accepted)
            return True
        else:
            self.logger.warning("The entered number does not match the student number format",
                                extra={"user": chat_id, "number": number})
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
        if not text.strip():
            self.logger.warning("Empty text for post", extra={"user": chat_id, "img": img_id})
            self.bot.send_message(chat_id=chat_id, text=empty_post_text)
            return
        if is_admin(chat_id):
            self.set_article(chat_id, text, img_id)
            self.logger.info("Post successfully created or modified",
                             extra={"user": chat_id, "text": text, "img": img_id})
            self.bot.send_message(chat_id=chat_id, text=data_accepted)
            self.set_admin_categories_markup(chat_id)
        else:
            self.logger.warning("Unauthorized attempt to create a post",
                                extra={"user": chat_id, "text": text, "img": img_id})
            self.bot.send_message(chat_id=chat_id, text=not_admin)

    def handle_keyboard(self, chat_id, text, message_id):
        self.logger.debug("Start handling student keyboard", extra={"user": chat_id, "message_id": message_id})
        if text == find:
            self.logger.debug("Start handling student publish button",
                              extra={"user": chat_id, "message_id": message_id})
            self.kh.handle_find_btn(chat_id, message_id)
        elif text in self.ms.categories:
            self.logger.debug("Start handling student categories",
                              extra={"user": chat_id, "message_id": message_id, "text": text})
            self.kh.handle_category_btn(chat_id, message_id, text)
        elif text == back:
            self.logger.debug("Start handling student back button", extra={"user": chat_id, "message_id": message_id})
            self.kh.handle_back_btn(chat_id, message_id)
        else:
            self.logger.debug("Start handling student tags",
                              extra={"user": chat_id, "message_id": message_id, "text": text})
            self.kh.handle_tag_btn(chat_id, message_id, text)
        self.logger.debug("End handling student keyboard", extra={"user": chat_id, "message_id": message_id})

    def handle_admin_keyboard(self, chat_id, text, message_id):
        self.logger.debug("Start handling admin keyboard", extra={"user": chat_id, "message_id": message_id})
        if text == publish:
            self.logger.debug("Start handling admin publish button", extra={"user": chat_id, "message_id": message_id})
            self.akh.handle_post_btn(chat_id, message_id)
        elif text in self.ams.admin_categories:
            self.logger.debug("Start handling admin categories",
                              extra={"user": chat_id, "message_id": message_id, "text": text})
            self.akh.handle_admin_category_btn(chat_id, message_id, text)
        elif text == back:
            self.logger.debug("Start handling admin back button", extra={"user": chat_id, "message_id": message_id})
            self.akh.handle_admin_back_btn(chat_id, message_id)
        else:
            self.logger.debug("Start handling admin tags",
                              extra={"user": chat_id, "message_id": message_id, "text": text})
            self.akh.handle_admin_tag_btn(chat_id, message_id, text)
        self.logger.debug("End handling admin keyboard", extra={"user": chat_id, "message_id": message_id})

    def create_categories_markup(self, chat_id):
        if is_admin(chat_id):
            return self.ams.create_categories_markup()
        else:
            return self.ms.create_categories_markup()

    def help_hint(self, chat_id):
        if is_admin(chat_id):
            self.bot.send_message(chat_id, help_admin)
        else:
            self.bot.send_message(chat_id, help_student)
