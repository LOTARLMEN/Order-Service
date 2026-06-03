from pydantic import BaseModel

from app.core.models import Item, OrderStatusEnum


class OrderDTO(BaseModel):
    user_id: str
    item: Item
    status: OrderStatusEnum
