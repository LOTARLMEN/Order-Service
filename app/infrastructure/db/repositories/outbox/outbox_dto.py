from pydantic import BaseModel


class OutboxDTO(BaseModel):
    event_type: str
    payload: dict
