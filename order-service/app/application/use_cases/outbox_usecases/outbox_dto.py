from app.core.models import OrderEventType, OutboxEventStatus
from pydantic import BaseModel


class OutboxEventDTO(BaseModel):
    event_type: OrderEventType
    payload: dict
    status: OutboxEventStatus
