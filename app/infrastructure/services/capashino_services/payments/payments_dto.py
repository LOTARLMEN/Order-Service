from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PaymentDTO(BaseModel):
    order_id: UUID
    amount: Decimal
    callback_url: str
    idempotency_key: str | UUID
