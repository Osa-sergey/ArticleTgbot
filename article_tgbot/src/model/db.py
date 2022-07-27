import logging

import psycopg2
import psycopg2.pool
from psycopg2 import OperationalError

from settings.settings import *
from settings.settings import LOGGER
from tools.meta_class import MetaSingleton


class DB(metaclass=MetaSingleton):

    def __init__(self):
        self.logger = logging.getLogger(LOGGER)
        try:
            if IS_DEBUG:
                self.con_pool = psycopg2.pool.ThreadedConnectionPool(DB_MIN_CON, DB_MAX_CON,
                                                                     user=DB_USER,
                                                                     password=DB_PASSWORD,
                                                                     host=DB_HOST,
                                                                     port=DB_PORT,
                                                                     database=DB_NAME)
                self.logger.info("DB connection in DEBUG mode")
            else:
                self.con_pool = psycopg2.pool.ThreadedConnectionPool(DB_MIN_CON, DB_MAX_CON,
                                                                     user=DB_USER,
                                                                     password=DB_PASSWORD,
                                                                     host=DB_HOST,
                                                                     database=DB_NAME)
                self.logger.info("DB connection in PRODUCTION mode")
        except OperationalError:
            self.logger.exception("A error occurred while connecting to the database")
            self.con_pool = None

    def execute_query(self, query, params):
        con = self.con_pool.getconn()
        con.autocommit = True
        cursor = con.cursor()
        try:
            cursor.execute(query, params)
            cursor.close()
        except Exception:
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
        except Exception:
            self.logger.exception("A error occurred while executing query with returned results")
        finally:
            self.con_pool.putconn(con)
