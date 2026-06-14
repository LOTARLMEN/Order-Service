from typing import Any, AsyncContextManager, Protocol, runtime_checkable
from uuid import UUID

from app.application.dto.kafka import KafkaProducerDTO
from app.application.dto.notifications import NotificationDTO
from app.application.dto.payments import PaymentDTO
from app.application.use_cases.order_usecases.order_dto import OrderDTO
from app.application.use_cases.outbox_usecases.outbox_dto import OutboxEventDTO
from app.application.use_cases.process_shipping_event.inbox_dto import InboxEventDTO
from app.core.models import InboxEvent, Item, Order, OrderStatusEnum, OutboxEvent


@runtime_checkable
class ICatalogServiceClient(Protocol):
    async def get_item(self, item_id: UUID) -> Item: ...


@runtime_checkable
class IPaymentServiceClient(Protocol):
    async def create_payment(self, payment_dto: PaymentDTO) -> dict: ...


@runtime_checkable
class INotificationsServiceClient(Protocol):
    async def send_notification(self, notification: NotificationDTO) -> dict: ...


@runtime_checkable
class IKafkaProducerService(Protocol):
    async def send_message(self, producer_dto: KafkaProducerDTO): ...


@runtime_checkable
class IOrderRepository(Protocol):
    async def create(self, order: OrderDTO) -> Order | None: ...
    async def get_by_id(self, order_id: UUID) -> Order | Any: ...
    async def update_status(
        self, order_id: UUID, status: OrderStatusEnum
    ) -> Order | None: ...


@runtime_checkable
class IOutboxRepository(Protocol):
    async def create(self, event: OutboxEventDTO) -> OutboxEvent | None: ...
    async def get_pending_events(
        self, limit: int = 100
    ) -> list[OutboxEvent | None]: ...
    async def get_by_id(self, event_id: UUID) -> OutboxEvent | None: ...
    async def update(self, event_id: UUID): ...


@runtime_checkable
class IInboxRepository(Protocol):
    async def create(self, event: InboxEventDTO) -> InboxEvent: ...
    async def exists(self, event: InboxEventDTO) -> bool: ...


@runtime_checkable
class IIdempotencyKeyRepository(Protocol):
    async def create(self, key: str): ...
    async def get(self, key: str) -> Any: ...
    async def set_response(self, key: str, response: dict): ...


@runtime_checkable
class IUnitOfWorkImplementation(Protocol):
    @property
    def orders(self) -> IOrderRepository: ...
    @property
    def outbox(self) -> IOutboxRepository: ...
    @property
    def inbox(self) -> IInboxRepository: ...
    @property
    def idempotency_key(self) -> IIdempotencyKeyRepository: ...

    async def commit(self): ...


@runtime_checkable
class IUnitOfWork(Protocol):
    def __call__(self) -> AsyncContextManager[IUnitOfWorkImplementation]: ...
