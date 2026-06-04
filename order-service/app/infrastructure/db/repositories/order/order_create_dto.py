from uuid import UUID

from app.application.use_cases.order_usecases.order_dto import OrderResponseDTO
from pydantic import BaseModel


class OrderCreateRequestSchema(BaseModel):
    user_id: str
    quantity: int
    item_id: UUID
    idempotency_key: UUID


class OrderResponseSchema(OrderResponseDTO): ...
