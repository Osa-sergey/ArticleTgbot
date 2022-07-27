import logging.config

LOG_FILENAME = "logs\\log.txt"
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "for_server_logs": {
            "format": "[%(asctime)s]  %(levelname)s  (%(filename)s:%(funcName)s:%(lineno)d) %(message)s",
            "datefmt": "%y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console_output": {
            "formatter": "for_server_logs",
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file_output":  {
            "formatter": "for_server_logs",
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILENAME,
        }

    },
    "loggers": {
        "article_tgbot": {
            "level": "DEBUG",
            "handlers": [
                "console_output",
                "file_output",
            ],
        },

    },
}


def logger_configure():
    logging.config.dictConfig(LOGGING_CONFIG)