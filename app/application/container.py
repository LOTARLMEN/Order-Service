from dependency_injector import containers, providers

from app.application.use_cases.outbox_usecases.outbox_events_usecase import (
    OutboxEventsUseCase,
)
from app.application.use_cases.process_shipping_event.shipping_event import (
    ProcessShippingEventUseCase,
)
from app.infrastructure.container import InfrastructureContainer
from app.infrastructure.services.kafka.consumers.shipping import ShippingEventConsumer


class ApplicationContainer(containers.DeclarativeContainer):
    setting = providers.Configuration()

    infrastructure_container = providers.Container[InfrastructureContainer](
        InfrastructureContainer,
        setting=setting,
    )

    unit_of_work = infrastructure_container.unit_of_work
    outbox_events_use_case = providers.Singleton[OutboxEventsUseCase](
        OutboxEventsUseCase,
        unit_of_work=unit_of_work,
    )
    process_shipping_event_use_case = providers.Singleton[ProcessShippingEventUseCase](
        ProcessShippingEventUseCase,
        unit_of_work=unit_of_work,
    )

    shipping_consumer = providers.Singleton[ShippingEventConsumer](
        ShippingEventConsumer,
        url=setting.Kafka.BOOTSTRAP_SERVERS,
        process_shipping_event_use_case=process_shipping_event_use_case,
    )
