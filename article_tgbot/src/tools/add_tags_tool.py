import yaml
from yaml.loader import SafeLoader

from model.db import *
from model.sql_queries import insert_tags_query


def init_tags():
    db = DB()
    with open(os.path.dirname(__file__) + '/../../res/new_tags.yaml', encoding='utf-8') as f:
        data = yaml.load(f, Loader=SafeLoader)
    for i in data:
        for category, v in i.items():
            for value in v:
                db.execute_query(insert_tags_query,
                                 (value, category))
