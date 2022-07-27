import logging

from keyboa import Keyboa

from settings.text_settings import selected_tag
from model.data_layer import DataLayer
from settings.settings import LOGGER
from tools.meta_class import MetaSingleton


class MarkupService(metaclass=MetaSingleton):

    def __init__(self):
        self.dl = DataLayer()
        self.logger = logging.getLogger(__name__)
        self.categories = self.get_categories()
        self.tags = self.get_tags(self.categories)

    def create_categories_markup(self):
        return Keyboa(items=list(self.categories), copy_text_to_callback=True).keyboard

    def create_tags_markup(self, category, chat_id):
        index = self.categories.index(category)
        items = list(self.tags[index])
        marked_tags = self.dl.get_marked_tags(category, chat_id)
        for i in range(len(items) - 1):
            if items[i] in marked_tags:
                items[i] = items[i] + selected_tag
        return Keyboa(items=items).keyboard

    def get_categories(self):
        categories = self.dl.get_all_categories()
        categories.append("Найти")
        categories = tuple(categories)
        self.logger.info(f"Student categories were created. categories: {categories}")
        return categories

    def get_tags(self, categories):
        buttons = ["Назад", "Найти"]
        tags = []
        for category in categories:
            if category != "Найти":
                row_tags = self.dl.get_tags_by_category(category)
                row_tags.append(buttons)
                row_tags = tuple(row_tags)
                tags.append(row_tags)
        self.logger.info(f"Student tags were created. tags: {tags}")
        return tuple(tags)
