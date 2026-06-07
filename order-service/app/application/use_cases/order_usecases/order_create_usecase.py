import logging
from uuid import UUID

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
from app.infrastructure.db.repositories.idempotency_key.exceptions import (
    IdempotencyKeyAlreadyExistsError,
)
from app.infrastructure.db.repositories.order.exceptions import (
    ItemNotEnoughException,
)
from app.infrastructure.db.repositories.order.order_create_dto import (
    OrderCreateRequestSchema,
)
from app.infrastructure.services.capashino_services.catalog import CatalogServiceClient
from app.infrastructure.services.capashino_services.notifications.notifications import (
    NotificationsServiceClient,
)
from app.infrastructure.services.capashino_services.notifications.notifications_dto import (
    NotificationDTO,
)
from app.infrastructure.services.capashino_services.payments.payments import (
    PaymentServiceClient,
)
from app.infrastructure.services.capashino_services.payments.payments_dto import (
    PaymentDTO,
)
from app.infrastructure.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class CreateOrderUseCase(BaseUseCase):
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        catalog_service: CatalogServiceClient,
        payment_service: PaymentServiceClient,
        notification_service: NotificationsServiceClient,
    ):
        super().__init__(unit_of_work)
        self._catalog = catalog_service
        self._payment = payment_service
        self._notification = notification_service

    async def __call__(self, order_dto: OrderCreateRequestSchema) -> OrderResponseDTO:

        logger.info("Order dto: {}".format(order_dto.model_dump()))
        item = await self._catalog.get_item(order_dto.item_id)
        logger.info("Item from catalog service: {}".format(item.model_dump()))

        if item.available_qty < order_dto.quantity:
            raise ItemNotEnoughException("Not enough items.")

        async with self._unit_of_work() as uow:
            try:
                await uow.idempotency_key.create(order_dto.idempotency_key)
            except IdempotencyKeyAlreadyExistsError:
                existing = await uow.idempotency_key.get(order_dto.idempotency_key)

                if existing and existing.response:
                    return OrderResponseDTO.model_validate(existing.response)

                raise IdempotencyKeyExistException("Idempotency key already exist.")

            order = await uow.orders.create(
                OrderDTO(
                    user_id=order_dto.user_id,
                    item=item.model_dump(),
                    quantity=order_dto.quantity,
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
                    payload=response.model_dump(mode="json"),
                    status=OutboxEventStatus.PENDING,
                )
            )

            await uow.idempotency_key.set_response(
                order_dto.idempotency_key,
                response.model_dump(mode="json"),
            )

            try:
                # Step 4: Send notification for NEW status
                await self._notification.send_notification(
                    NotificationDTO(
                        user_id=order.user_id,
                        message="Ваш заказ создан и ожидает оплаты",
                        reference_id=str(order.id),
                        idempotency_key="{}_new".format(order_dto.idempotency_key),
                    )
                )
            except Exception as e:
                logger.error("Failed to send notification: %s", str(e))

            try:
                # Step 2: Create payment
                await self._payment.create_payment(
                    PaymentDTO(
                        order_id=order.id,
                        amount=item.price * order_dto.quantity,
                        idempotency_key=order_dto.idempotency_key,
                    )
                )
            except Exception as e:
                logger.error("Failed to create payment: %s", str(e))
                # Update status to CANCELLED if payment creation fails
                await uow.orders.update_status(
                    order_id=order.id, status=OrderStatusEnum.CANCELLED
                )
                response.status = OrderStatusEnum.CANCELLED

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
