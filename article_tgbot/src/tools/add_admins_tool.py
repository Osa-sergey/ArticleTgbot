import yaml
from yaml.loader import SafeLoader

from article_tgbot.src.model.db import *
from article_tgbot.src.model.sql_queries import insert_admins_query


def init_admins():
    db = DB()
    with open('res/new_admins.yaml', encoding='utf-8') as f:
        data = yaml.load(f, Loader=SafeLoader)
    for i in data:
        db.execute_query(insert_admins_query,
                         (i,))
