from uuid import UUID

from pydantic import BaseModel

from app.application.use_cases.order_usecases.order_dto import OrderResponseDTO


class OrderCreateRequestSchema(BaseModel):
    user_id: str
    quantity: int
    item_id: UUID
    idempotency_key: str


class OrderResponseSchema(OrderResponseDTO): ...
