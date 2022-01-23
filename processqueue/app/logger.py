import logging
import logging.config
import os
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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    logging.setLogRecordFactory(LogRecordFactory)
    logger = logging.getLogger(f"{module_name}")
    return logger
