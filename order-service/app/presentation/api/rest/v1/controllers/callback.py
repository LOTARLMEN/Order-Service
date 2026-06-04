from fastapi import APIRouter

from .callback_dto import PaymentCallbackDTO

router = APIRouter(prefix="/payment-callback")


@router.post("")
async def process_payment_callback(callback: PaymentCallbackDTO): ...
