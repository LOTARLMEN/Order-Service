from decimal import Decimal

from pydantic import BaseModel

from app.core.models import Item, OrderStatusEnum


class OrderDTO(BaseModel):
    user_id: str
    items: list[Item]
    amount: Decimal
    status: OrderStatusEnum
