from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.models import Item, OrderStatusEnum


class OrderDTO(BaseModel):
    user_id: str
    item: Item
    status: OrderStatusEnum


class OrderResponseDTO(BaseModel):
    id: UUID
    user_id: str
    quantity: int
    item_id: UUID
    status: OrderStatusEnum
    created_at: datetime
    update_at: datetime
