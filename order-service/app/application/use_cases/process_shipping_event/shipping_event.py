import logging
from uuid import UUID

from app.application.use_cases.base import BaseUseCase
from app.application.use_cases.exceptions import (
    OrderNotExistsException,
)
from app.application.use_cases.process_shipping_event.inbox_dto import InboxEventDTO
from app.core.models import OrderEventType, OrderStatusEnum
from app.infrastructure.services.capashino_services.notifications.notifications import (
    NotificationsServiceClient,
)
from app.infrastructure.services.capashino_services.notifications.notifications_dto import (
    NotificationDTO,
)
from app.infrastructure.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class ProcessShippingEventUseCase(BaseUseCase):
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        notification_service: NotificationsServiceClient,
    ):
        super().__init__(unit_of_work)
        self._notification = notification_service

    async def __call__(self, order_id: UUID, event_type: str):
        async with self._unit_of_work() as uow:
            event_dto = InboxEventDTO(
                order_id=order_id,
                event_type=event_type,
            )
            if await uow.inbox.exists(event=event_dto):
                logger.warning(
                    "Event %s for order %s already exists", event_type, order_id
                )
                return

            await uow.inbox.create(event=event_dto)

            order = await uow.orders.get_by_id(order_id=order_id)

            if not order:
                raise OrderNotExistsException("Order not found.")

            notification_msg = None
            if event_type == OrderEventType.ORDER_SHIPPED:
                new_status = OrderStatusEnum.SHIPPED
                notification_msg = "SHIPPED: Ваш заказ отправлен в доставку"
            elif event_type == OrderEventType.ORDER_CANCELLED:
                new_status = OrderStatusEnum.CANCELLED
                notification_msg = "CANCELLED: Ваш заказ отменен. Причина: Insufficient stock"  # Default reason for shipping cancellation
            else:
                return

            await uow.orders.update_status(
                order_id=order.id,
                status=new_status,
            )

            try:
                if notification_msg:
                    await self._notification.send_notification(
                        NotificationDTO(
                            user_id=order.user_id,
                            message=notification_msg,
                            reference_id=str(order.id),
                            idempotency_key="{}_{}".format(
                                order.id, new_status.lower()
                            ),
                        )
                    )
            except Exception as e:
                logger.error("Failed to send notification: %s", str(e))

            await uow.commit()
