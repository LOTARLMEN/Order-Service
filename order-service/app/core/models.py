from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class Payment(BaseModel):
    id: UUID
    user_id: str
    order_id: str
    amount: Decimal
    idempotency_key: str
    created_at: datetime


class Notification(BaseModel):
    id: UUID
    user_id: UUID
    message: str
    reference_id: UUID
    created_at: datetime


class Item(BaseModel):
    id: UUID
    name: str
    price: Decimal
    available_qty: int
    created_at: datetime

    @property
    def get_amount(self) -> Decimal:
        return self.price * self.available_qty


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
    item: Item
    quantity: int
    status: OrderStatusEnum
    created_at: datetime
    status_history: list[OrderStatusHistory]


class OrderEventType(StrEnum):
    ORDER_CREATED = "order.created"
    ORDER_PAID = "order.paid"
    ORDER_SHIPPED = "order.shipped"
    ORDER_CANCELLED = "order.cancelled"
    NOTIFICATION_SEND = "notification.send"


class OutboxEventStatus(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"


class OutboxEvent(BaseModel):
    id: UUID
    event_type: OrderEventType
    payload: dict
    status: OutboxEventStatus
    created_at: datetime


class InboxEvent(BaseModel):
    order_id: UUID
    event_type: OrderEventType
    created_at: datetime
