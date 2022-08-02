import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
LOCALHOST = "localhost"
DB_HOST = os.getenv('DB_HOST', LOCALHOST)
IS_DEBUG = True if DB_HOST == LOCALHOST else False
DB_PORT = 5433
DB_MIN_CON = 5
DB_MAX_CON = 20
TAG_FOR_ALL_STUDENTS = os.getenv('TAG_FOR_ALL_STUDENTS')
LOGGER = "article_tgbot"


