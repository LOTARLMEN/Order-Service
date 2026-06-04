from app.config.base_setting import BaseConfig
from pydantic_settings import SettingsConfigDict


class KafkaConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="KAFKA_")

    BOOTSTRAP_SERVERS: str
