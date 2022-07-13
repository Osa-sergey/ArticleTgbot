import re
from keyboa import Keyboa

from model.data_layer import DataLayer
from tags import *


class LogicLayer:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(LogicLayer, cls).__new__(cls)
        return cls.__instance

    def __init__(self, bot):
        self.bot = bot
        self.dl = DataLayer()

    def init_university_id_and_tags(self, message):
        if not self.save_university_id(message):
            return
        self.tags_command(message)

    def tags_command(self, message):
        markup = self.create_categories_markup()
        self.bot.send_message(message.chat.id,
                              "Выберите нужные теги и нажмите найти",
                              reply_markup=markup)

    def save_university_id(self, message):
        number = message.text
        chat_id = message.chat.id
        pattern = r'^[m]{0,1}[0-9]{7}$'
        res = re.search(pattern, number)
        if res is not None:
            self.bot.send_message(chat_id, "Номер удачно внесен")
            stud_number = res.group(0)
            if len(stud_number) == 8:
                stud_number = stud_number[1:]
            self.dl.set_university_id(chat_id, stud_number)
            return True
        else:
            self.bot.send_message(chat_id, "Введен неправильный формат номера. Формат m******* или без m")
            return False

    def handle_find_btn(self, chat_id, message_id):
        print("Конец настройки")
        if not self.dl.has_user_university_id(chat_id):
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text="Вы не ввели номер студенческого билета."
                                            " Воспользуйтесь /student_number или /start")
        elif not self.dl.has_marked_tags(chat_id):
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text="Выберите хотя бы один тег")
        else:
            articles = self.dl.get_articles(chat_id)
            print(articles)
            for article in articles:
                if article[1]:
                    print(article)
                    self.bot.send_photo(chat_id=chat_id,
                                        caption=article[0],
                                        photo=article[1])
                else:
                    self.bot.send_message(chat_id=chat_id,
                                          text=article[0])

    def handle_category_btn(self, chat_id, message_id, category_name):
        print("Категория")
        markup = self.create_tags_markup(category_name, chat_id, False)
        self.bot.edit_message_text(chat_id=chat_id,
                                   message_id=message_id,
                                   text=category_name,
                                   reply_markup=markup)

    def handle_back_btn(self, chat_id, message_id):
        print("Назад")
        markup = self.create_categories_markup(False)
        self.bot.edit_message_text(chat_id=chat_id,
                                   message_id=message_id,
                                   text="Выберите нужные теги и нажмите найти",
                                   reply_markup=markup)

    def handle_tag_btn(self, chat_id, message_id, tag_name):
        print("Теги")
        emoji_index = tag_name.find(" ✅")
        if emoji_index != -1:
            tag_name = tag_name[:emoji_index]
        print(tag_name)
        self.dl.set_tag_to_student(chat_id, tag_name)
        category = self.dl.get_category_by_tag(tag_name)
        markup = self.create_tags_markup(category, chat_id, False)
        self.bot.edit_message_text(chat_id=chat_id,
                                   message_id=message_id,
                                   text=category,
                                   reply_markup=markup)

    def handle_post_btn(self, chat_id, message_id):
        print("Публикация")
        article = self.dl.post_article(chat_id)
        if article:
            self.bot.edit_message_text(chat_id=chat_id,
                                       message_id=message_id,
                                       text="Успешная публикация")
            article_id = article[0]
            article_text = article[1]
            article_img = article[2]
            print(article_id)
            approp_students = self.dl.get_approp_students(article_id)
            print(approp_students)
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
                                  text="У статьи нет тегов")

    def handle_admin_category_btn(self, chat_id, message_id, category_name):
        print("Категория")
        article_id = self.dl.get_article_id(chat_id)
        markup = self.create_tags_markup(category_name, article_id, True)
        self.bot.edit_message_text(chat_id=chat_id,
                                   message_id=message_id,
                                   text=category_name,
                                   reply_markup=markup)

    def handle_admin_back_btn(self, chat_id, message_id):
        print("Назад")
        markup = self.create_categories_markup(True)
        self.bot.edit_message_text(chat_id=chat_id,
                                   message_id=message_id,
                                   text="Выберите нужные теги и нажмите опубликовать",
                                   reply_markup=markup)

    def handle_admin_tag_btn(self, chat_id, message_id, tag_name):
        print("Теги")
        emoji_index = tag_name.find(" ✅")
        if emoji_index != -1:
            tag_name = tag_name[:emoji_index]
        print(tag_name)
        article_id = self.dl.get_article_id(chat_id)
        print(article_id)
        self.dl.set_tag_to_article(article_id, tag_name)
        category = self.dl.get_category_by_tag(tag_name)
        markup = self.create_tags_markup(category, article_id, True)
        self.bot.edit_message_text(chat_id=chat_id,
                                   message_id=message_id,
                                   text=category,
                                   reply_markup=markup)

    def create_categories_markup(self, user_id):
        if self.is_admin(user_id):
            return Keyboa(items=list(categories_admin), copy_text_to_callback=True).keyboard
        else:
            return Keyboa(items=list(categories), copy_text_to_callback=True).keyboard

    def create_tags_markup(self, category, chat_id, is_admin):
        print(category)
        if is_admin:
            index = categories_admin.index(category)
            items = list(tags_admin[index])
            marked_tags = self.dl.get_admin_marked_tags(category, chat_id)
        else:
            index = categories.index(category)
            items = list(tags[index])
            marked_tags = self.dl.get_marked_tags(category, chat_id)
        print(f"marked_tags '{marked_tags}'")
        for i in range(len(items) - 1):
            print(items[i])
            if items[i] in marked_tags:
                items[i] = items[i] + " ✅"
        return Keyboa(items=items).keyboard

    def set_admin_categories_markup(self, chat_id):
        markup = self.create_categories_markup(True)
        self.bot.send_message(chat_id=chat_id,
                              text="Выберите нужные теги и нажмите опубликовать",
                              reply_markup=markup)

    def is_admin_lambda(self, call):
        return self.is_admin(call.message.chat.id)

    def is_admin(self, user_id):
        return self.dl.is_user_admin(user_id)

    def set_article(self, chat_id, text, img_id):
        self.dl.set_text_and_img_to_article(chat_id, text, img_id)
