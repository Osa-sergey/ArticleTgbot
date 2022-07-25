import logging

import psycopg2
import psycopg2.pool

from settings.settings import *


class DB:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(DB, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            self.con_pool = psycopg2.pool.ThreadedConnectionPool(DB_MIN_CON, DB_MAX_CON,
                                                                 user=DB_USER,
                                                                 password=DB_PASSWORD,
                                                                 host=DB_HOST,
                                                                 database=DB_NAME)
        except (Exception, psycopg2.DatabaseError):
            self.logger.exception("A error occurred while connecting to the database")
            self.con_pool = None

    def execute_query(self, query, params):
        con = self.con_pool.getconn()
        con.autocommit = True
        cursor = con.cursor()
        try:
            cursor.execute(query, params)
            cursor.close()
        except BaseException:
            self.logger.exception("A error occurred while executing query without returned results")
        finally:
            self.con_pool.putconn(con)

    def execute_query_with_result(self, query, params):
        con = self.con_pool.getconn()
        con.autocommit = True
        cursor = con.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except BaseException:
            self.logger.exception("A error occurred while executing query with returned results")
        finally:
            self.con_pool.putconn(con)
