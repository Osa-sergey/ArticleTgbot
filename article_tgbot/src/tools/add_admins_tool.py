import yaml
from yaml.loader import SafeLoader

from model.db import *
from model.sql_queries import insert_admins_query


def init_admins():
    db = DB()
    with open(os.path.dirname(__file__) + '/../../res/new_admins.yaml', encoding='utf-8') as f:
        data = yaml.load(f, Loader=SafeLoader)
    for i in data:
        db.execute_query(insert_admins_query,
                         (i,))
