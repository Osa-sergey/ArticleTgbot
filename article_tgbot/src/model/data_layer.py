import logging

from article_tgbot.src.model.db import DB
from article_tgbot.src.model.sql_queries import *
from article_tgbot.settings.settings import TAG_FOR_ALL_STUDENTS


class DataLayer:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(DataLayer, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.db = DB()
        self.logger = logging.getLogger(__name__)

    def _has_result(self, method, params):
        result = self.db.execute_query_with_result(method, params)
        if result:
            return True
        else:
            return False

    def has_user_university_id(self, chat_id):
        return self._has_result(has_university_id_query, (chat_id,))

    def has_marked_tags(self, chat_id):
        return self._has_result(has_marked_tags_query, (chat_id,))

    def is_user_admin(self, chat_id):
        return self._has_result(has_admin_permissions_query, (chat_id,))

    def get_articles(self, chat_id):
        return self.db.execute_query_with_result(get_articles_query,
                                                 (chat_id,))

    def get_approp_students(self, article_id):
        is_for_all = self.db.execute_query_with_result(is_article_for_all_query,
                                                       (article_id, TAG_FOR_ALL_STUDENTS))
        if len(is_for_all) == 1:
            self.logger.info(f"The post broadcasted. post_id: {article_id}")
            return self.db.execute_query_with_result(get_all_students_query,
                                                     ())
        else:
            return self.db.execute_query_with_result(get_students_for_article_query,
                                                     (article_id,))

    def set_university_id(self, chat_id, stud_number):
        self.db.execute_query(create_or_update_university_id_query,
                              (chat_id, stud_number, stud_number))

    def set_tag_to_student(self, chat_id, tag_name):
        self.db.execute_query(set_tag_to_student_query,
                              (chat_id, tag_name))

    def set_tag_to_article(self, article_id, tag_name):
        self.db.execute_query(set_tag_to_article_query,
                              (article_id, tag_name))

    def set_text_and_img_to_article(self, chat_id, text, img_id):
        self.db.execute_query(set_text_and_img_to_article_query,
                              (chat_id, text, img_id))

    def get_article_id(self, chat_id):
        res = self.db.execute_query_with_result(get_article_id_query,
                                                (chat_id,))
        return res[0][0]

    def get_category_by_tag(self, tag):
        res = self.db.execute_query_with_result(get_category_by_tag_query,
                                                (tag,))
        return res[0][0]

    def get_marked_tags(self, category, chat_id):
        res = self.db.execute_query_with_result(get_student_marked_tags_query,
                                                (chat_id, category))
        if res:
            return res[0]
        else:
            return []

    def post_article(self, chat_id):
        res = self.db.execute_query_with_result(post_article_query,
                                                (chat_id,))
        if res:
            return res[0]
        else:
            return []

    def get_admin_marked_tags(self, category, article_id):
        res = self.db.execute_query_with_result(get_article_marked_tags_query,
                                                (article_id, category))
        if res:
            return [x for t in res for x in t]
        else:
            return []

    def get_all_categories(self,):
        res = self.db.execute_query_with_result(get_all_categories_query, ())
        res = [x for t in res for x in t]
        return res

    def get_tags_by_category(self, category):
        res = self.db.execute_query_with_result(get_tags_by_category_query, (category,))
        return [x for t in res for x in t]
