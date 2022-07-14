from controller.service.admin.admin_markup_service import AdminMarkupService
from model.data_layer import DataLayer
from settings.text_settings import *


class AdminKeyHandlerService:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(AdminKeyHandlerService, cls).__new__(cls)
        return cls.__instance

    def __init__(self, bot):
        self.bot = bot
        self.dl = DataLayer()
        self.mkp = AdminMarkupService()

    def handle_post_btn(self, chat_id, message_id):
        article = self.dl.post_article(chat_id)
        if article:
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text=success_publishing)
            article_id = article[0]
            article_text = article[1]
            article_img = article[2]
            approp_students = self.dl.get_approp_students(article_id)
            if article_img:
                for student in approp_students:
                    self.bot.send_photo(chat_id=student[0],
                                        caption=article_text,
                                        photo=article_img)
            else:
                for student in approp_students:
                    self.bot.send_message(chat_id=student[0],
                                          text=article_text)
        else:
            self.bot.send_message(chat_id=chat_id,
                                  text=article_hasnt_tags)

    def handle_admin_category_btn(self, chat_id, message_id, category_name):
        article_id = self.dl.get_article_id(chat_id)
        markup = self.mkp.create_tags_markup(category_name, article_id)
        self.bot.edit_message_text(chat_id=chat_id,
                                   message_id=message_id,
                                   text=category_name,
                                   reply_markup=markup)

    def handle_admin_back_btn(self, chat_id, message_id):
        markup = self.mkp.create_categories_markup()
        self.bot.edit_message_text(chat_id=chat_id,
                                   message_id=message_id,
                                   text=tags_choose_and_publish,
                                   reply_markup=markup)

    def handle_admin_tag_btn(self, chat_id, message_id, tag_name):
        emoji_index = tag_name.find(selected_tag)
        if emoji_index != -1:
            tag_name = tag_name[:emoji_index]
        article_id = self.dl.get_article_id(chat_id)
        self.dl.set_tag_to_article(article_id, tag_name)
        category = self.dl.get_category_by_tag(tag_name)
        markup = self.mkp.create_tags_markup(category, article_id)
        self.bot.edit_message_text(chat_id=chat_id,
                                   message_id=message_id,
                                   text=category,
                                   reply_markup=markup)
