from pydantic import BaseModel

from app.config.database import DatabaseConfig
from app.config.kafka import KafkaConfig
from app.config.service import CapashinoConfig


class Settings(BaseModel):
    Database: DatabaseConfig = DatabaseConfig()
    Capashino: CapashinoConfig = CapashinoConfig()
    Kafka: KafkaConfig = KafkaConfig()


if __name__ == "__main__":
    settings = Settings()
    print(settings)
