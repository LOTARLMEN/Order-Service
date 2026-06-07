import logging
from uuid import UUID

from app.application.use_cases.base import BaseUseCase
from app.application.use_cases.order_usecases.exceptions import OrderNotFoundException
from app.application.use_cases.outbox_usecases.outbox_dto import OutboxEventDTO
from app.core.models import OrderEventType, OrderStatusEnum, OutboxEventStatus
from app.infrastructure.services.capashino_services.notifications.notifications_dto import (
    NotificationDTO,
)
from app.presentation.api.rest.v1.controllers.callback.callback_dto import (
    PaymentCallbackDTO,
)

logger = logging.getLogger(__name__)


class ProcessPaymentCallbackUseCase(BaseUseCase):
    async def __call__(self, callback_dto: PaymentCallbackDTO):
        async with self._unit_of_work() as uow:
            order_id = UUID(callback_dto.order_id)
            order = await uow.orders.get_by_id(order_id)

            if not order:
                raise OrderNotFoundException("Order {} not found.".format(order_id))

            if order.status != OrderStatusEnum.NEW:
                logger.info(
                    "Order %s already processed with status %s", order_id, order.status
                )
                return

            if callback_dto.status == "succeeded":
                new_status = OrderStatusEnum.PAID
                notification_msg = "PAID: Ваш заказ успешно оплачен и готов к отправке"

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
                notification_msg = "CANCELLED: Ваш заказ отменен. Причина: {}".format(
                    reason
                )

            await uow.orders.update_status(order_id=order.id, status=new_status)

            await uow.outbox.create(
                OutboxEventDTO(
                    idempotency_key="{}_{}".format(order.id, new_status.lower()),
                    event_type=OrderEventType.NOTIFICATION_SEND,
                    payload=NotificationDTO(
                        user_id=order.user_id,
                        message=notification_msg,
                        reference_id=str(order.id),
                        idempotency_key="{}_{}".format(order.id, new_status.lower()),
                    ).model_dump(mode="json"),
                    status=OutboxEventStatus.PENDING,
                )
            )

            await uow.commit()
