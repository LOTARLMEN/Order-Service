from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.config.config import settings


class PaymentDTO(BaseModel):
    order_id: UUID
    amount: Decimal
    callback_url: str = settings.OrderService.SHIPPING_URL
    idempotency_key: str | UUID
