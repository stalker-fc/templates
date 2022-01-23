import logging
import logging.config
import os
import sys
from logging import Logger


class LogRecordFactory(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.environment = os.environ.get('ENVIRONMENT', 'local')
        self._process = self.process
        self._thread = self.threadName
        self._module = self.module
        self.function = self.funcName
        self.line = self.lineno


def get_logger(module_name: str) -> Logger:
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "common": {
                "format": "%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "common",
                "stream": sys.stdout
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "INFO",
            },
        }
    }
    logging.config.dictConfig(config)
    logging.setLogRecordFactory(LogRecordFactory)
    logger = logging.getLogger(f"{module_name}")
    return logger
