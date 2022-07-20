import yaml
from yaml.loader import SafeLoader

from article_tgbot.src.model.db import *
from article_tgbot.src.model.sql_queries import insert_tags_query


def init_tags():
    db = DB()
    with open('res/new_tags.yaml', encoding='utf-8') as f:
        data = yaml.load(f, Loader=SafeLoader)
    for i in data:
        for category, v in i.items():
            for value in v:
                db.execute_query(insert_tags_query,
                                 (value, category))
