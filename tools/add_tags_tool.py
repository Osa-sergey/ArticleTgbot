import yaml
from yaml.loader import SafeLoader

from db import *
from sql_queries import insert_tags_query

if __name__ == '__main__':
    db = DB()
    with open('../scripts/new_tags.yaml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    for i in data:
        for category, v in i.items():
            for value in v:
                db.execute_query(insert_tags_query,
                                 (value, category))
