import logging.config


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(message)s"
        },
    },
    "handlers": {
        "console_output": {
            "formatter": "simple",
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "article_tgbot": {
            "level": "DEBUG",
            "handlers": [
                "console_output"
            ],
        },

    },
}


def logger_configure():
    logging.config.dictConfig(LOGGING_CONFIG)
