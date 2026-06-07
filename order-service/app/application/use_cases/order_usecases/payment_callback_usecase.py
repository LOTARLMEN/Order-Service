import logging
from uuid import UUID

from app.application.use_cases.base import BaseUseCase
from app.application.use_cases.order_usecases.exceptions import OrderNotFoundException
from app.application.use_cases.outbox_usecases.outbox_dto import OutboxEventDTO
from app.core.models import OrderEventType, OrderStatusEnum, OutboxEventStatus
from app.infrastructure.services.capashino_services.notifications.notifications import (
    NotificationsServiceClient,
)
from app.infrastructure.services.capashino_services.notifications.notifications_dto import (
    NotificationDTO,
)
from app.infrastructure.unit_of_work import UnitOfWork
from app.presentation.api.rest.v1.controllers.callback.callback_dto import (
    PaymentCallbackDTO,
)

logger = logging.getLogger(__name__)


class ProcessPaymentCallbackUseCase(BaseUseCase):
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        notification_service: NotificationsServiceClient,
    ):
        super().__init__(unit_of_work)
        self._notification = notification_service

    async def __call__(self, callback_dto: PaymentCallbackDTO):
        async with self._unit_of_work() as uow:
            order_id = UUID(callback_dto.order_id)
            order = await uow.orders.get_by_id(order_id)

            if not order:
                raise OrderNotFoundException("Order {} not found.".format(order_id))

            # Idempotency: if already processed, do nothing
            if order.status != OrderStatusEnum.NEW:
                logger.info(
                    "Order %s already processed with status %s", order_id, order.status
                )
                return

            if callback_dto.status == "succeeded":
                new_status = OrderStatusEnum.PAID
                notification_msg = "Ваш заказ успешно оплачен и готов к отправке"

                # Step 3: Add outbox event for order.paid
                await uow.outbox.create(
                    OutboxEventDTO(
                        idempotency_key="{}_paid".format(order.id),
                        event_type=OrderEventType.ORDER_PAID,
                        payload={
                            "event_type": OrderEventType.ORDER_PAID,
                            "order_id": str(order.id),
                            "item_id": str(order.item.id),
                            "quantity": order.quantity,
                            "idempotency_key": str(order.id),
                        },
                        status=OutboxEventStatus.PENDING,
                    )
                )
            else:
                new_status = OrderStatusEnum.CANCELLED
                reason = callback_dto.error_message or "Payment failed"
                notification_msg = "Ваш заказ отменен. Причина: {}".format(reason)

            await uow.orders.update_status(order_id=order.id, status=new_status)

            try:
                # Step 4: Send notification
                await self._notification.send_notification(
                    NotificationDTO(
                        user_id=order.user_id,
                        message=notification_msg,
                        reference_id=str(order.id),
                        idempotency_key="{}_{}".format(order.id, new_status.lower()),
                    )
                )
            except Exception as e:
                logger.error("Failed to send notification: %s", str(e))

            await uow.commit()
