import logging

from prometheus_client import Counter

from model.data_layer import DataLayer
from settings.settings import LOGGER, ID
from settings.text_settings import *
from tools.meta_class import MetaSingleton
from .markup_service import MarkupService


class KeyHandlerService(metaclass=MetaSingleton):
    btn_find_prom_counter = Counter('tgbot_btn_find_searches_total',
                                    'The total number of searches for new config of tags',
                                    ["identifier"])

    def __init__(self, bot):
        self.bot = bot
        self.dl = DataLayer()
        self.mkp = MarkupService()
        self.logger = logging.getLogger(LOGGER)

    def handle_find_btn(self, chat_id, message_id):
        if not self.dl.has_user_university_id(chat_id):
            self.logger.warning(f"User: {chat_id} hasn't student number. message_id: {message_id}")
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text=add_student_number)
        elif not self.dl.has_marked_tags(chat_id):
            self.logger.warning(f"User: {chat_id} hasn't selected tags. message_id: {message_id}")
            markup = self.mkp.create_categories_markup()
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text=choose_at_least_one_tag,
                                       reply_markup=markup)
        else:
            markup = self.mkp.create_bin_choice_tags_markup()
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text=search_tags_question,
                                       reply_markup=markup)

    def handle_bin_choice_tags_btn(self, chat_id, message_id, text):
        if text == yes_tags:
            markup = self.mkp.create_bin_choice_article_markup()
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text="Показывать вакансии за последние 3 недели?",
                                       reply_markup=markup)
        if text == no_tags:
            self.logger.info(f"Choose addition tags for search. student: {chat_id}, message_id: {message_id}")
            markup = self.mkp.create_categories_markup()
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text=tags_choose_and_search,
                                       reply_markup=markup)

    def handle_bin_choice_articles_btn(self, chat_id, message_id, text):
        self.btn_find_prom_counter.labels(ID).inc()
        if text == yes_articles:
            articles = self.dl.get_articles(chat_id)
            self.logger.debug(f"Student: {chat_id} has {len(articles)} for selected tags. message_id: {message_id}")
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text=search_counter + f" {len(articles)}",
                                       reply_markup="")
            for article in articles:
                if article[1]:
                    self.bot.send_photo(chat_id=chat_id,
                                        caption=article[0],
                                        photo=article[1])
                else:
                    self.bot.send_message(chat_id=chat_id,
                                          text=article[0])
            self.logger.debug(f"Finish handling student find button. student: {chat_id}, message_id: {message_id}")
        if text == no_articles:
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text=wait_new_articles,
                                       reply_markup="")
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
