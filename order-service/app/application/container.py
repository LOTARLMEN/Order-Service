from dependency_injector import containers, providers

from app.application.use_cases.order_usecases.order_create_usecase import (
    CreateOrderUseCase,
    GetOrderUseCase,
)
from app.application.use_cases.order_usecases.payment_callback_usecase import (
    ProcessPaymentCallbackUseCase,
)
from app.application.use_cases.outbox_usecases.outbox_events_usecase import (
    OutboxEventsUseCase,
)
from app.application.use_cases.process_shipping_event.shipping_event import (
    ProcessShippingEventUseCase,
)
from app.infrastructure.container import InfrastructureContainer
from app.infrastructure.services.kafka.consumers.shipping import ShippingEventConsumer


class ApplicationContainer(containers.DeclarativeContainer):
    settings = providers.Configuration()

    infrastructure_container = providers.Container[InfrastructureContainer](
        InfrastructureContainer,
        settings=settings,
    )

    unit_of_work = infrastructure_container.unit_of_work
    outbox_events_use_case = providers.Singleton[OutboxEventsUseCase](
        OutboxEventsUseCase,
        unit_of_work=unit_of_work,
        kafka_producer=infrastructure_container.kafka_producer,
    )
    process_shipping_event_use_case = providers.Singleton[ProcessShippingEventUseCase](
        ProcessShippingEventUseCase,
        unit_of_work=unit_of_work,
        notification_service=infrastructure_container.notification_service,
    )

    create_order_use_case = providers.Singleton[CreateOrderUseCase](
        CreateOrderUseCase,
        unit_of_work=unit_of_work,
        catalog_service=infrastructure_container.catalog_service,
        payment_service=infrastructure_container.payment_service,
        notification_service=infrastructure_container.notification_service,
    )

    get_order_use_case = providers.Singleton[GetOrderUseCase](
        GetOrderUseCase,
        unit_of_work=unit_of_work,
    )

    process_payment_callback_use_case = providers.Singleton[
        ProcessPaymentCallbackUseCase
    ](
        ProcessPaymentCallbackUseCase,
        unit_of_work=unit_of_work,
        notification_service=infrastructure_container.notification_service,
    )

    shipping_consumer = providers.Singleton[ShippingEventConsumer](
        ShippingEventConsumer,
        url=settings.Kafka.BOOTSTRAP_SERVERS,
        process_shipping_event_use_case=process_shipping_event_use_case,
    )
