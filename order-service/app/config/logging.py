from typing import Literal

from pydantic_settings import BaseSettings


class LoggingConfig(BaseSettings):
    LOG_FORMAT: str = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    LEVEL: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"
