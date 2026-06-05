from uuid import UUID

from pydantic import BaseModel

from app.core.models import OrderEventType, OutboxEventStatus


class OutboxEventDTO(BaseModel):
    idempotency_key: UUID
    event_type: OrderEventType
    payload: dict
    status: OutboxEventStatus
