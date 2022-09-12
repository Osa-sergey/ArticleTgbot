import logging

import psycopg2
import psycopg2.pool
from psycopg2 import OperationalError
from prometheus_client import Counter, Summary, Gauge

from settings.settings import *
from settings.settings import LOGGER
from tools.meta_class import MetaSingleton


class DB(metaclass=MetaSingleton):
    query_prom_summary = Summary('tgbot_db_query_latency_seconds',
                                 'Time to serve queries without result to db')
    query_with_result_prom_summary = Summary('tgbot_db_query_with_result_latency_seconds',
                                             'Time to serve queries with result to db')
    query_err_prom_counter = Counter('tgbot_db_query_errors_total',
                                     'Total number of errors non result queries to db')
    query_with_result_err_prom_counter = Counter('tgbot_db_query_with_result_errors_total',
                                                 'Total number of errors queries with result to db')
    con_err_prom_counter = Counter('tgbot_db_connection_error_total',
                                   'Total number error connections to db')
    con_number_prom_gauge = Gauge('tgbot_db_active_connections_total',
                                  'Total number of active connections to db')

    def __init__(self):
        self.logger = logging.getLogger(LOGGER)
        try:
            if IS_DEBUG:
                self.con_pool = psycopg2.pool.ThreadedConnectionPool(DB_MIN_CON, DB_MAX_CON,
                                                                     user=DB_USER,
                                                                     password=DB_PASSWORD,
                                                                     host=DB_HOST,
                                                                     port=DB_PORT,
                                                                     database=DB_NAME,
                                                                     options=f"-c search_path={DB_SCHEMA}")
                self.logger.info("DB connection in DEBUG mode")
            else:
                self.con_pool = psycopg2.pool.ThreadedConnectionPool(DB_MIN_CON, DB_MAX_CON,
                                                                     user=DB_USER,
                                                                     password=DB_PASSWORD,
                                                                     host=DB_HOST,
                                                                     database=DB_NAME,
                                                                     options=f"-c search_path={DB_SCHEMA}")
                self.logger.info("DB connection in PRODUCTION mode")
        except OperationalError:
            self.con_err_prom_counter.inc()
            self.logger.exception("A error occurred while connecting to the database")
            self.con_pool = None

    @query_prom_summary.time()
    def execute_query(self, query, params):
        con = self.con_pool.getconn()
        self.con_number_prom_gauge.inc()
        con.autocommit = True
        cursor = con.cursor()
        try:
            cursor.execute(query, params)
            cursor.close()
        except Exception:
            self.query_err_prom_counter.inc()
            self.logger.exception("A error occurred while executing query without returned results")
        finally:
            self.con_pool.putconn(con)
            self.con_number_prom_gauge.dec()

    @query_with_result_prom_summary.time()
    def execute_query_with_result(self, query, params):
        con = self.con_pool.getconn()
        self.con_number_prom_gauge.inc()
        con.autocommit = True
        cursor = con.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception:
            self.query_with_result_err_prom_counter.inc()
            self.logger.exception("A error occurred while executing query with returned results")
        finally:
            self.con_pool.putconn(con)
            self.con_number_prom_gauge.dec()
