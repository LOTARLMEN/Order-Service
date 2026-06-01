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


class EventTypeEnum(StrEnum):
    ORDER_CREATED = "ORDER.CREATED"


class OutboxEventStatus(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"


class OutboxEvent(BaseModel):
    id: UUID
    event_type: EventTypeEnum
    payload: dict
    status: OutboxEventStatus
    created_at: datetime
