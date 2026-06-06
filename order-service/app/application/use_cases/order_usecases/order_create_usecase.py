from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.application.use_cases.base import BaseUseCase
from app.application.use_cases.order_usecases.exceptions import (
    IdempotencyKeyExistException,
    OrderNotFoundException,
)
from app.application.use_cases.order_usecases.order_dto import (
    OrderDTO,
    OrderResponseDTO,
)
from app.application.use_cases.outbox_usecases.outbox_dto import OutboxEventDTO
from app.core.models import OrderEventType, OrderStatusEnum, OutboxEventStatus
from app.infrastructure.db.repositories.order.exceptions import (
    ItemNotEnoughException,
)
from app.infrastructure.db.repositories.order.order_create_dto import (
    OrderCreateRequestSchema,
)
from app.infrastructure.services.capashino_services.catalog import CatalogServiceClient
from app.infrastructure.unit_of_work import UnitOfWork


class CreateOrderUseCase(BaseUseCase):
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        catalog_service: CatalogServiceClient,
    ):
        super().__init__(unit_of_work)
        self._catalog = catalog_service

    async def __call__(self, order_dto: OrderCreateRequestSchema) -> OrderResponseDTO:
        item = await self._catalog.get_item(order_dto.item_id)

        if item.available_qty < order_dto.quantity:
            raise ItemNotEnoughException("Not enough items.")

        async with self._unit_of_work() as uow:
            try:
                await uow.idempotency.create(order_dto.idempotency_key)
            except IntegrityError:
                existing = await uow.idempotency_key.get(order_dto.idempotency_key)

                if existing and existing.response:
                    return OrderResponseDTO.model_validate(existing.response)

                raise IdempotencyKeyExistException()

            order = await uow.orders.create(
                OrderDTO(
                    user_id=order_dto.user_id,
                    item=item,
                    status=OrderStatusEnum.NEW,
                )
            )

            response = OrderResponseDTO(
                id=order.id,
                user_id=order.user_id,
                quantity=order_dto.quantity,
                item_id=order.item.id,
                status=order.status,
                created_at=order.created_at,
                update_at=order.status_history[0].created_at,
            )

            await uow.outbox.create(
                OutboxEventDTO(
                    idempotency_key=order_dto.idempotency_key,
                    event_type=OrderEventType.ORDER_CREATED,
                    payload=response.model_dump(),
                    status=OutboxEventStatus.PENDING,
                )
            )

            await uow.idempotency.set_response(
                order_dto.idempotency_key,
                response.model_dump(),
            )

            await uow.commit()

        return response


class GetOrderUseCase(BaseUseCase):
    async def __call__(self, order_id: UUID) -> OrderResponseDTO:
        async with self._unit_of_work() as uow:
            order = await uow.orders.get_by_id(order_id)

            if not order:
                raise OrderNotFoundException("Order {} not found.".format(order_id))

            order_to_response = OrderResponseDTO(
                id=order.id,
                user_id=order.user_id,
                quantity=order.item.available_qty,
                item_id=order.item.id,
                status=order.status,
                created_at=order.created_at,
                update_at=order.status_history[0].created_at,
            )

            return order_to_response
