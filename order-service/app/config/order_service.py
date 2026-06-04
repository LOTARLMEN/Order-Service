from app.config.base_setting import BaseConfig
from pydantic_settings import SettingsConfigDict


class OrderAppConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="ORDER_")

    SERVICE_NAME: str
    SERVICE_HOST: str
    SERVICE_PORT: int
