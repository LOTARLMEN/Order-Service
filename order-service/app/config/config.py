from pydantic import BaseModel

from app.config.capashino import CapashinoConfig
from app.config.database import DatabaseConfig
from app.config.kafka import KafkaConfig
from app.config.logging import LoggingConfig
from app.config.order_service import OrderAppConfig


class Settings(BaseModel):
    Database: DatabaseConfig = DatabaseConfig()
    Capashino: CapashinoConfig = CapashinoConfig()
    Kafka: KafkaConfig = KafkaConfig()
    OrderService: OrderAppConfig = OrderAppConfig()
    Logging: LoggingConfig = LoggingConfig()


settings = Settings()
