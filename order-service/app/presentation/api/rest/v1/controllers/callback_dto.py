from decimal import Decimal

from pydantic import BaseModel


class PaymentCallbackDTO(BaseModel):
    payment_id: str
    order_id: str
    status: str
    amount: Decimal
    error_message: str | None = None
