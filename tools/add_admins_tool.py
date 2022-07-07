import yaml
from yaml.loader import SafeLoader

from db import *
from settings import *

if __name__ == '__main__':
    con = create_connection(db_name, db_user, db_password, db_host, db_port)
    with open('../scripts/new_admins.yaml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    for i in data:
        execute_query(con,
                      insert_admins_query,
                      (i,))
    con.close()
