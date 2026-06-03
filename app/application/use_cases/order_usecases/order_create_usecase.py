from app.application.use_cases.base import BaseUseCase
from app.application.use_cases.order_usecases.exceptions import (
    OrderFailedCreateException,
    OutboxEventFailedCreateException,
)
from app.application.use_cases.order_usecases.order_dto import OrderDTO
from app.application.use_cases.outbox_usecases.outbox_dto import OutboxEventDTO
from app.core.models import Order, OrderEventType, OrderStatusEnum, OutboxEventStatus
from app.infrastructure.db.repositories.order.exceptions import (
    ItemNotEnoughException,
    NotItemException,
)
from app.infrastructure.db.repositories.order.order_create_dto import OrderCreateDTO
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

    async def __call__(self, order_dto: OrderCreateDTO):
        async with self._unit_of_work() as uow:
            item = await self._catalog.get_item(order_dto.item_id)

            if item.qnt < order_dto.quantity:
                raise ItemNotEnoughException("Not enough items.")

            if item.qnt == 0:
                raise NotItemException

            order_to_db = OrderDTO(
                user_id=order_dto.user_id,
                item=item,
                status=OrderStatusEnum.NEW,
            )

            order: Order = await uow.orders.create(order_to_db)
            if not order:
                raise OrderFailedCreateException("Failed to create order.")

            outbox_event_to_db = OutboxEventDTO(
                event_type=OrderEventType.ORDER_CREATED,
                payload=order.model_dump(),
                status=OutboxEventStatus.PENDING,
            )
            outbox_event = await uow.outbox.create(outbox_event_to_db)
            if not outbox_event:
                raise OutboxEventFailedCreateException("Failed to create outbox event.")

            await uow.commit()
