import psycopg2
from psycopg2 import OperationalError

categories = ("IT", "Металлургия", "Нефтянка", "Продажи", "Найти")
tags = (("ИТКН", ["Назад", "Найти"]),
        ("ИНМИН", ["Назад", "Найти"]),
        (["Назад", "Найти"]),
        (["Назад", "Найти"]))

categories_admin = ("IT", "Металлургия", "Нефтянка", "Продажи", "Опубликовать")
tags_admin = (("ИТКН", ["Назад", "Опубликовать"]),
              ("ИНМИН", ["Назад", "Опубликовать"]),
              (["Назад", "Опубликовать"]),
              (["Назад", "Опубликовать"]))

update_university_id_query = """INSERT INTO target_article.student (telegram_id, university_id)
                                VALUES (%s, %s)
                                ON CONFLICT (telegram_id)
                                DO UPDATE SET university_id = %s"""

insert_tags_query = """INSERT INTO target_article.tag (tag_name, category)
                       VALUES (%s, %s)
                       ON CONFLICT (tag_name)
                       DO NOTHING"""

has_university_id_query = """ SELECT 1 FROM target_article.student 
                              WHERE telegram_id = %s AND university_id IS NOT NULL"""

has_marked_tags_query = """SELECT 1 FROM target_article.students_to_tags WHERE student_id = %s """

get_articles_query = """SELECT * FROM target_article.get_articles_for_student(%s)"""

get_category_by_tag_query = """SELECT tag.category
                               FROM target_article.tag AS tag
                               WHERE tag_name = %s"""

get_student_marked_tags_query = """SELECT tag.tag_name
                           FROM target_article.students_to_tags stt
                           INNER JOIN target_article.tag as tag ON stt.tag_name_id = tag.tag_name
                           WHERE stt.student_id = %s AND tag.category = %s"""

set_tag_to_student_query = """SELECT * FROM target_article.set_tag_to_student(%s, %s)"""

get_students_for_article_query = """SELECT * FROM target_article.get_students_for_article(%s)"""

post_article_query = """SELECT * FROM target_article.post_article(%s)"""

set_text_and_img_to_article_query = """SELECT * FROM target_article.set_text_and_img_to_article(%s, %s, %s)"""

has_admin_permissions_query = """SELECT 1 FROM target_article.admins WHERE id = %s"""

set_tag_to_article_query = """SELECT * FROM target_article.set_tag_to_article(%s, %s)"""

get_article_marked_tags_query = """SELECT tag.tag_name
                                   FROM target_article.tags_to_articles tta
                                   INNER JOIN target_article.tag as tag ON tta.tag_name_id = tag.tag_name
                                   WHERE tta.article_id = %s AND tag.category = %s"""

get_article_id_query = """SELECT id FROM target_article.article
                    WHERE is_posted = FALSE AND id_who_created = %s
                    ORDER BY date
                    LIMIT 1"""


def create_connection(name, user, password, host, port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=name,
            user=user,
            password=password,
            host=host,
            port=port
        )
    except OperationalError as e:
        print(f"Connection error '{e}'")
    return connection


def execute_query(connection, query, params):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        cursor.close()
    except BaseException as e:
        print(f"The error '{e}' occurred")


def execute_query_with_result(connection, query, params):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result
    except BaseException as e:
        print(f"The error '{e}' occurred")
        return ()


def get_category_by_tag(tag, connection):
    res = execute_query_with_result(connection,
                                    get_category_by_tag_query,
                                    (tag,))
    return res[0][0]
