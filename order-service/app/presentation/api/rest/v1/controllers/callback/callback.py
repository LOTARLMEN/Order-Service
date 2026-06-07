import logging
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.application.use_cases.order_usecases.payment_callback_usecase import (
    ProcessPaymentCallbackUseCase,
)
from app.presentation.container import PresentationContainer

from .callback_dto import PaymentCallbackDTO

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orders/payment-callback")


@router.post("")
@inject
async def process_payment_callback(
    callback: PaymentCallbackDTO,
    use_case: ProcessPaymentCallbackUseCase = Depends(
        Provide[
            PresentationContainer.application_container.process_payment_callback_use_case
        ]
    ),
):
    logger.info(
        "Received payment callback for order %s: %s", callback.order_id, callback.status
    )
    await use_case(callback)
    return {"status": "ok"}
