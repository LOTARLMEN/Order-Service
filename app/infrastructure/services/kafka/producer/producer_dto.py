from pydantic import BaseModel


class KafkaProducerDTO(BaseModel):
    topic: str
    key: str | None = None
    msg: dict
