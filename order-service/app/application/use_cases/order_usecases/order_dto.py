from datetime import datetime
from uuid import UUID

from app.core.models import Item, OrderStatusEnum
from pydantic import BaseModel


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
