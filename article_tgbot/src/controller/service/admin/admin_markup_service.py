import logging

from keyboa import Keyboa

from article_tgbot.settings.text_settings import selected_tag
from article_tgbot.src.model.data_layer import DataLayer


class AdminMarkupService:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(AdminMarkupService, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.dl = DataLayer()
        self.logger = logging.getLogger(__name__)
        self.admin_categories = self.get_admin_categories()
        self.admin_tags = self.get_admin_tags(self.admin_categories)

    def create_categories_markup(self):
        return Keyboa(items=list(self.admin_categories), copy_text_to_callback=True).keyboard

    def create_tags_markup(self, category, chat_id):
        index = self.admin_categories.index(category)
        items = list(self.admin_tags[index])
        marked_tags = self.dl.get_admin_marked_tags(category, chat_id)
        for i in range(len(items) - 1):
            if items[i] in marked_tags:
                items[i] = items[i] + selected_tag
        return Keyboa(items=items).keyboard

    def get_admin_categories(self):
        categories = self.dl.get_all_categories()
        categories.append("Опубликовать")
        categories = tuple(categories)
        self.logger.info("Admin categories were created", extra={"categories": categories})
        return categories

    def get_admin_tags(self, categories):
        buttons = ["Назад", "Опубликовать"]
        tags = []
        for category in categories:
            if category != "Опубликовать":
                row_tags = self.dl.get_tags_by_category(category)
                row_tags.append(buttons)
                row_tags = tuple(row_tags)
                tags.append(row_tags)
        self.logger.info("Admin tags were created", extra={"tags": tags})
        return tuple(tags)
