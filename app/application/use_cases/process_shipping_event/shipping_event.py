from uuid import UUID

from app.application.use_cases.base import BaseUseCase
from app.application.use_cases.exceptions import (
    EventAlreadyExistsException,
    OrderNotExistsException,
)
from app.application.use_cases.process_shipping_event.inbox_dto import InboxEventDTO
from app.core.models import InboxEventTypeEnum, OrderStatusEnum


class ProcessShippingEventUseCase(BaseUseCase):
    async def __call__(self, order_id: UUID, event_type: str):
        async with self._unit_of_work() as uow:
            event_dto = InboxEventDTO(
                order_id=order_id,
                event_type=event_type,
            )
            if await uow.inbox.exists(event=event_dto):
                raise EventAlreadyExistsException("Event already exists.")

            event = await uow.inbox.create(event=event_dto)

            order = await uow.orders.get_by_id(order_id=event.order_id)

            if not order:
                raise OrderNotExistsException("Order not found.")

            if event_type == InboxEventTypeEnum.ORDER_SHIPPED:
                order.status = OrderStatusEnum.SHIPPED
            elif event_type == InboxEventTypeEnum.ORDER_CANCELLED:
                order.status = OrderStatusEnum.CANCELLED

            await uow.orders.update_status(
                order_id=order.id,
                status=order.status,
            )
            await uow.commit()
