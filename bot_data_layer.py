from db import *


def has_user_university_id(chat_id, connection):
    result = execute_query_with_result(connection,
                                       has_university_id_query,
                                       (chat_id,))
    if result:
        return True
    else:
        return False


def has_marked_tags(chat_id, connection):
    result = execute_query_with_result(connection,
                                       has_marked_tags_query,
                                       (chat_id,))
    if result:
        return True
    else:
        return False


def get_articles(chat_id, connection):
    return execute_query_with_result(connection,
                                     get_articles_query,
                                     (chat_id,))


def get_marked_tags(category, chat_id, connection):
    res = execute_query_with_result(connection,
                                    get_student_marked_tags_query,
                                    (chat_id, category))
    if res:
        return res[0]
    else:
        return []


def set_university_id(chat_id, stud_number, connection):
    execute_query(connection,
                  update_university_id_query,
                  (chat_id, stud_number, stud_number))


def set_tag_to_student(chat_id, tag_name, connection):
    execute_query(connection,
                  set_tag_to_student_query,
                  (chat_id, tag_name))


def post_article(chat_id, connection):
    res = execute_query_with_result(connection,
                                    post_article_query,
                                    (chat_id,))
    if res:
        return res[0]
    else:
        return []


def get_approp_students(article_id, connection):
    return execute_query_with_result(connection,
                                     get_students_for_article_query,
                                     (article_id,))


def get_article_id(chat_id, connection):
    res = execute_query_with_result(connection,
                                    get_article_id_query,
                                    (chat_id,))
    return res[0][0]


def set_tag_to_article(article_id, tag_name, connection):
    execute_query(connection,
                  set_tag_to_article_query,
                  (article_id, tag_name))


def get_admin_marked_tags(category, article_id, connection):
    res = execute_query_with_result(connection,
                                    get_article_marked_tags_query,
                                    (article_id, category))
    if res:
        return res[0]
    else:
        return []


def is_user_admin(chat_id, connection):
    res = execute_query_with_result(connection,
                                    has_admin_permissions_query,
                                    (chat_id,))
    if res:
        return True
    else:
        return False


def is_user_admin_lambda(call):
    connection = create_connection(db_name, db_user, db_password, db_host, db_port)
    res = execute_query_with_result(connection,
                                    has_admin_permissions_query,
                                    (call.message.chat.id,))
    connection.close()
    if res:
        return True
    else:
        return False


def set_text_and_img_to_article(chat_id, text, img_id, connection):
    execute_query(connection,
                  set_text_and_img_to_article_query,
                  (chat_id, text, img_id))


def get_category_by_tag(tag, connection):
    res = execute_query_with_result(connection,
                                    get_category_by_tag_query,
                                    (tag,))
    return res[0][0]
