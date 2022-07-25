import logging

from .markup_service import MarkupService
from model.data_layer import DataLayer
from settings.text_settings import *


class KeyHandlerService:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(KeyHandlerService, cls).__new__(cls)
        return cls.__instance

    def __init__(self, bot):
        self.bot = bot
        self.dl = DataLayer()
        self.mkp = MarkupService()
        self.logger = logging.getLogger(__name__)

    def handle_find_btn(self, chat_id, message_id):
        if not self.dl.has_user_university_id(chat_id):
            self.logger.warning(f"User: {chat_id} hasn't student number. message_id: {message_id}")
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text=add_student_number)
        elif not self.dl.has_marked_tags(chat_id):
            self.logger.warning(f"User: {chat_id} hasn't selected tags. message_id: {message_id}")
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text=choose_at_least_one_tag)
        else:
            articles = self.dl.get_articles(chat_id)
            self.logger.debug(f"Student: {chat_id} has {len(articles)} for selected tags. message_id: {message_id}")
            for article in articles:
                if article[1]:
                    self.bot.send_photo(chat_id=chat_id,
                                        caption=article[0],
                                        photo=article[1])
                else:
                    self.bot.send_message(chat_id=chat_id,
                                          text=article[0])
        self.logger.debug(f"Finish handling student find button. student: {chat_id}, message_id: {message_id}")

    def handle_category_btn(self, chat_id, message_id, category_name):
        markup = self.mkp.create_tags_markup(category_name, chat_id)
        self.bot.edit_message_text(chat_id=chat_id,
                                   message_id=message_id,
                                   text=category_name,
                                   reply_markup=markup)

    def handle_back_btn(self, chat_id, message_id):
        markup = self.mkp.create_categories_markup()
        self.bot.edit_message_text(chat_id=chat_id,
                                   message_id=message_id,
                                   text=tags_choose_and_search,
                                   reply_markup=markup)
        self.logger.debug(f"Finish handling student back button. student: {chat_id}, message_id: {message_id}")

    def handle_tag_btn(self, chat_id, message_id, tag_name):
        emoji_index = tag_name.find(selected_tag)
        if emoji_index != -1:
            tag_name = tag_name[:emoji_index]
        self.dl.set_tag_to_student(chat_id, tag_name)
        self.logger.info(f"The status of the tag: {tag_name} has been changed for the student: {chat_id}")
        category = self.dl.get_category_by_tag(tag_name)
        markup = self.mkp.create_tags_markup(category, chat_id)
        self.bot.edit_message_text(chat_id=chat_id,
                                   message_id=message_id,
                                   text=category,
                                   reply_markup=markup)
        self.logger.debug(f"Finish handling student tags. student: {chat_id}, message_id: {message_id}")
