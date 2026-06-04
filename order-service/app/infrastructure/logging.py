import logging
import sys

from app.config.config import settings


def setup_logging():
    log_level = getattr(logging, settings.logger.LOG_LEVEL)
    log_format = settings.logger.LOG_FORMAT
    date_format = settings.logger.LOG_DATE_FORMAT

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
