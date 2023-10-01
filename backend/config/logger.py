LOGGING = {
    "version": 1,  # the dictConfig format version
    "disable_existing_loggers": False,  # retain the default loggers
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",  # Format for the timestamp
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "backend": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "login": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "register": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "accounts": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "files": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "django.channels.server": {
            "level": "INFO",
            "handlers": ["console"],
        },
    },
}
