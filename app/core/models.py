from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class Item(BaseModel):
    id: str
    name: str
    price: Decimal


class OrderStatusEnum(StrEnum):
    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class OrderStatusHistory(BaseModel):
    status: OrderStatusEnum
    created_at: datetime


class Order(BaseModel):
    id: UUID
    user_id: str
    items: list[Item]
    amount: Decimal
    status: OrderStatusEnum
    status_history: list[OrderStatusHistory]


class OutboxEventTypeEnum(StrEnum):
    ORDER_CREATED = "order.created"


class OutboxEventStatus(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"


class OutboxEvent(BaseModel):
    id: UUID
    event_type: OutboxEventTypeEnum
    payload: dict
    status: OutboxEventStatus
    created_at: datetime


class InboxEventTypeEnum(StrEnum):
    ORDER_SHIPPED = "order.shipped"
    ORDER_CANCELLED = "order.cancelled"


class InboxEvent(BaseModel):
    order_id: UUID
    event_type: InboxEventTypeEnum
    created_at: datetime
