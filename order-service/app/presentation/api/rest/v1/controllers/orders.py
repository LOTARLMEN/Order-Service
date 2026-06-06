from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.application.use_cases.order_usecases.order_create_usecase import (
    CreateOrderUseCase,
    GetOrderUseCase,
)
from app.infrastructure.db.repositories.order.order_create_dto import (
    OrderCreateRequestSchema,
    OrderResponseSchema,
)
from app.presentation.container import PresentationContainer

router = APIRouter(prefix="/api/orders")


@router.post("", response_model=OrderResponseSchema, status_code=201)
@inject
async def create_order(
    order: OrderCreateRequestSchema,
    use_case: CreateOrderUseCase = Depends(
        Provide[PresentationContainer.application_container.create_order_use_case]
    ),
):
    return await use_case(order)


@router.get("/{order_id}", response_model=OrderResponseSchema)
@inject
async def get_order(
    order_id: UUID,
    use_case: GetOrderUseCase = Depends(
        Provide[PresentationContainer.application_container.get_order_use_case]
    ),
):
    return await use_case(order_id)
