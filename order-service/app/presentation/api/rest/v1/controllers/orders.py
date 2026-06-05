from http import HTTPStatus
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

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


@router.post("", response_model=OrderResponseSchema)
@inject
async def create_order(
    order: OrderCreateRequestSchema,
    use_case: CreateOrderUseCase = Depends(
        Provide[PresentationContainer.application_container.create_order_use_case]
    ),
):
    try:
        return await use_case(order)
    except Exception:
        return JSONResponse(
            content={"message": "Internal server error while creating order"},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@router.get("/{order_id}", response_model=OrderResponseSchema)
@inject
async def get_order(
    order_id: UUID,
    use_case: GetOrderUseCase = Depends(
        Provide[PresentationContainer.application_container.get_order_use_case]
    ),
):
    try:
        return await use_case(order_id)
    except Exception:
        return JSONResponse(
            content={"message": "Internal server error while getting order"},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
