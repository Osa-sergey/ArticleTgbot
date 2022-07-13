from keyboa import Keyboa

from model.data_layer import DataLayer
from tags import *


class MarkupService:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(MarkupService, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.dl = DataLayer()

    @staticmethod
    def create_categories_markup():
        return Keyboa(items=list(categories), copy_text_to_callback=True).keyboard

    def create_tags_markup(self, category, chat_id):
        index = categories.index(category)
        items = list(tags[index])
        marked_tags = self.dl.get_marked_tags(category, chat_id)
        for i in range(len(items) - 1):
            if items[i] in marked_tags:
                items[i] = items[i] + " ✅"
        return Keyboa(items=items).keyboard
