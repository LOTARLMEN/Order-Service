
from pydantic import BaseModel

from app.core.models import OrderEventType, OutboxEventStatus


class OutboxEventDTO(BaseModel):
    idempotency_key: str
    event_type: OrderEventType
    payload: dict
    status: OutboxEventStatus
