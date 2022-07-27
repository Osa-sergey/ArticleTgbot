import logging
import re

from controller.service.admin.admin_keyboard_handler_service import AdminKeyHandlerService
from controller.service.admin.admin_markup_service import AdminMarkupService
from controller.service.admin_check_service import is_admin
from controller.service.student.keyboard_handler_service import KeyHandlerService
from controller.service.student.markup_service import MarkupService
from model.data_layer import DataLayer
from settings.text_settings import *
from settings.settings import LOGGER
from tools.meta_class import MetaSingleton


class LogicLayer(metaclass=MetaSingleton):

    def __init__(self, bot):
        self.bot = bot
        self.dl = DataLayer()
        self.akh = AdminKeyHandlerService(bot)
        self.kh = KeyHandlerService(bot)
        self.ams = AdminMarkupService()
        self.ms = MarkupService()
        self.logger = logging.getLogger(LOGGER)

    def init_university_id_and_tags(self, message):
        if not self.save_university_id(message):
            return
        self.logger.info(f"Successful registration for student: {message.chat.id}")
        self.tags_command(message)

    def tags_command(self, message):
        chat_id = message.chat.id
        markup = self.create_categories_markup(chat_id)
        self.bot.send_message(chat_id, tags_choose_and_search, reply_markup=markup)

    def save_university_id(self, message):
        number = message.text
        chat_id = message.chat.id
        self.logger.debug(f"Number: {number} for check matching student number format for student: {chat_id}")
        pattern = r'^[m]{0,1}[0-9]{7}$'
        res = re.search(pattern, number)
        if res is not None:
            stud_number = res.group(0)
            self.logger.debug(f"Matched student number: {stud_number} for student: {chat_id}")
            if len(stud_number) == 8:
                stud_number = stud_number[1:]
            self.dl.set_university_id(chat_id, stud_number)
            self.logger.info(f"Successful saving of the student number for student: {chat_id}")
            self.bot.send_message(chat_id, student_number_accepted)
            return True
        else:
            self.logger.warning(f"The entered number: {number} does not match the student number format"
                                f" for student: {chat_id}")
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

    def create_or_edit_article(self, chat_id, text, message_id, img_id=""):
        if not text.strip():
            self.logger.warning(f"Empty text for post. admin: {chat_id}, img: {img_id}, message_id: {message_id}")
            self.bot.send_message(chat_id=chat_id, text=empty_post_text)
            return
        if is_admin(chat_id):
            self.set_article(chat_id, text, img_id)
            self.logger.info(f"Post successfully created or modified."
                             f" admin: {chat_id}, text: {text}, img: {img_id}, message_id: {message_id}")
            self.bot.send_message(chat_id=chat_id, text=data_accepted)
            self.set_admin_categories_markup(chat_id)
        else:
            self.logger.warning(f"Unauthorized attempt to create a post."
                                f" user: {chat_id}, text: {text}, img: {img_id}, message_id: {message_id}")
            self.bot.send_message(chat_id=chat_id, text=not_admin)

    def handle_keyboard(self, chat_id, text, message_id):
        if text == find:
            self.logger.debug(f"Start handling student find button. student: {chat_id}, message_id: {message_id}")
            self.kh.handle_find_btn(chat_id, message_id)
        elif text in self.ms.categories:
            self.kh.handle_category_btn(chat_id, message_id, text)
        elif text == back:
            self.logger.debug(f"Start handling student back button. student: {chat_id}, message_id: {message_id}")
            self.kh.handle_back_btn(chat_id, message_id)
        else:
            self.logger.debug(f"Start handling student tags."
                              f" student: {chat_id}, message_id: {message_id}, tag: {text}")
            self.kh.handle_tag_btn(chat_id, message_id, text)

    def handle_admin_keyboard(self, chat_id, text, message_id):
        if text == publish:
            self.logger.debug(f"Start handling admin publish button. admin: {chat_id}, message_id: {message_id}")
            self.akh.handle_post_btn(chat_id, message_id)
        elif text in self.ams.admin_categories:
            self.akh.handle_admin_category_btn(chat_id, message_id, text)
        elif text == back:
            self.logger.debug(f"Start handling admin back button. admin: {chat_id}, message_id: {message_id}")
            self.akh.handle_admin_back_btn(chat_id, message_id)
        else:
            self.logger.debug(f"Start handling admin tags. admin: {chat_id}, message_id: {message_id}, tag: {text}")
            self.akh.handle_admin_tag_btn(chat_id, message_id, text)

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

    def start_cmd(self, chat_id):
        if is_admin(chat_id):
            self.bot.send_message(chat_id, unallowable)
            self.logger.warning(f"Unallowable command: /start for administrator: {chat_id}")
        else:
            msg = self.bot.send_message(chat_id, start_student)
            self.logger.info(f"Start of new student: {chat_id} registration")
            self.bot.register_next_step_handler(msg, self.init_university_id_and_tags)

    def student_number_cmd(self, chat_id):
        if is_admin(chat_id):
            self.bot.send_message(chat_id, unallowable)
            self.logger.warning(f"Unallowable command: /student_number for administrator: {chat_id}")
        else:
            msg = self.bot.send_message(chat_id, student_number_student)
            self.logger.info(f"Start of enter student number. user: {chat_id}")
            self.bot.register_next_step_handler(msg, self.save_university_id)

    def tags_cmd(self, chat_id):
        if is_admin(chat_id):
            self.bot.send_message(chat_id, unallowable)
            self.logger.warning(f"Unallowable command: /tags for administrator: {chat_id}")
        else:
            markup = self.create_categories_markup(chat_id)
            self.bot.send_message(chat_id, tags_student, reply_markup=markup)
