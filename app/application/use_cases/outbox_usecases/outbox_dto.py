from pydantic import BaseModel


class OutboxEventDTO(BaseModel):
    event_type: str
    payload: dict
