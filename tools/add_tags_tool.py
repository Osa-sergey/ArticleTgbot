import yaml
from yaml.loader import SafeLoader

from tools import *
from settings import *

if __name__ == '__main__':
    con = create_connection(db_name, db_user, db_password, db_host, db_port)
    with open('../scripts/new_tags.yaml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    for i in data:
        for category, v in i.items():
            for value in v:
                execute_query(con,
                              insert_tags_query,
                              (value, category))
    con.close()
