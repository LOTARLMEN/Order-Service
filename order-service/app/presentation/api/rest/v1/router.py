from fastapi import APIRouter

from app.presentation.api.rest.v1.controllers.callback.callback import (
    router as callback_router,
)
from app.presentation.api.rest.v1.controllers.orders import router as orders_router

router = APIRouter(tags=["Заказы"])

router.include_router(orders_router)
router.include_router(callback_router)
