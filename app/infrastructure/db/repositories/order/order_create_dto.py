from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.models import OrderStatusEnum


class OrderCreateDTO(BaseModel):
    user_id: str
    quantity: int
    item_id: UUID
    idempotency_key: UUID


class OrderCreateRequestSchema(OrderCreateDTO):
    pass


class OrderCreateResponseSchema(BaseModel):
    id: UUID
    user_id: str
    quantity: int
    item_id: UUID
    status: OrderStatusEnum
    created_at: datetime
    update_at: datetime
