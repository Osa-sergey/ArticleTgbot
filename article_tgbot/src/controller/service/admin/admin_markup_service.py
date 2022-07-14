import logging

from keyboa import Keyboa

from article_tgbot.src.model.data_layer import DataLayer
from article_tgbot.src.tags import *


class AdminMarkupService:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(AdminMarkupService, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.dl = DataLayer()
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def create_categories_markup():
        return Keyboa(items=list(categories_admin), copy_text_to_callback=True).keyboard

    def create_tags_markup(self, category, chat_id):
        index = categories_admin.index(category)
        items = list(tags_admin[index])
        marked_tags = self.dl.get_admin_marked_tags(category, chat_id)
        for i in range(len(items) - 1):
            if items[i] in marked_tags:
                items[i] = items[i] + " ✅"
        return Keyboa(items=items).keyboard
