import yaml
from yaml.loader import SafeLoader

from db import *
from sql_queries import insert_admins_query

if __name__ == '__main__':
    db = DB()
    with open('../scripts/new_admins.yaml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    for i in data:
        db.execute_query(insert_admins_query,
                         (i,))
