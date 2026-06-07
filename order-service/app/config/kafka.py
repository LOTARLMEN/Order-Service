from pydantic_settings import SettingsConfigDict

from app.config.base_setting import BaseConfig


class KafkaConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="KAFKA_")

    BOOTSTRAP_SERVERS: str
    ORDER_EVENTS_TOPIC: str = "student_system-order.events"
    SHIPMENT_EVENTS_TOPIC: str = "student_system-shipment.events"
