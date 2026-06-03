from dependency_injector.wiring import inject
from fastapi import APIRouter

from app.infrastructure.db.repositories.order.order_create_dto import (
    OrderCreateRequestSchema,
    OrderCreateResponseSchema,
)

router = APIRouter()


@router.post("", response_model=OrderCreateResponseSchema)
@inject
async def create_order(
    order: OrderCreateRequestSchema,
): ...
