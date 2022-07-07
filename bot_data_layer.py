from db import DB
from sql_queries import *


class DataLayer:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(DataLayer, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.db = DB()

    def has_user_university_id(self, chat_id):
        result = self.db.execute_query_with_result(has_university_id_query,
                                                   (chat_id,))
        if result:
            return True
        else:
            return False

    def has_marked_tags(self, chat_id):
        result = self.db.execute_query_with_result(has_marked_tags_query,
                                                   (chat_id,))
        if result:
            return True
        else:
            return False

    def get_articles(self, chat_id):
        return self.db.execute_query_with_result(get_articles_query,
                                                 (chat_id,))

    def get_marked_tags(self, category, chat_id):
        res = self.db.execute_query_with_result(get_student_marked_tags_query,
                                                (chat_id, category))
        if res:
            return res[0]
        else:
            return []

    def set_university_id(self, chat_id, stud_number):
        self.db.execute_query(update_university_id_query,
                              (chat_id, stud_number, stud_number))

    def set_tag_to_student(self, chat_id, tag_name):
        self.db.execute_query(set_tag_to_student_query,
                              (chat_id, tag_name))

    def post_article(self, chat_id):
        res = self.db.execute_query_with_result(post_article_query,
                                                (chat_id,))
        if res:
            return res[0]
        else:
            return []

    def get_approp_students(self, article_id):
        return self.db.execute_query_with_result(get_students_for_article_query,
                                                 (article_id,))

    def get_article_id(self, chat_id):
        res = self.db.execute_query_with_result(get_article_id_query,
                                                (chat_id,))
        return res[0][0]

    def set_tag_to_article(self, article_id, tag_name):
        self.db.execute_query(set_tag_to_article_query,
                              (article_id, tag_name))

    def get_admin_marked_tags(self, category, article_id):
        res = self.db.execute_query_with_result(get_article_marked_tags_query,
                                                (article_id, category))
        if res:
            return res[0]
        else:
            return []

    def is_user_admin(self, chat_id):
        res = self.db.execute_query_with_result(has_admin_permissions_query,
                                                (chat_id,))
        if res:
            return True
        else:
            return False

    def is_user_admin_lambda(self, call):
        res = self.db.execute_query_with_result(has_admin_permissions_query,
                                                (call.message.chat.id,))
        if res:
            return True
        else:
            return False

    def set_text_and_img_to_article(self, chat_id, text, img_id):
        self.db.execute_query(set_text_and_img_to_article_query,
                              (chat_id, text, img_id))

    def get_category_by_tag(self, tag):
        res = self.db.execute_query_with_result(get_category_by_tag_query,
                                                (tag,))
        return res[0][0]
