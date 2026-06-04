from app.application.container import ApplicationContainer
from app.config.config import settings
from app.presentation.outbox_worker import OutboxWorker
from dependency_injector import containers, providers


class PresentationContainer(containers.DeclarativeContainer):
    settings = providers.Object(settings)

    application_container = providers.Container[ApplicationContainer](
        ApplicationContainer,
        settings=settings,
    )
    outbox_worker = providers.Singleton(
        OutboxWorker,
        outbox_events_use_case=application_container.outbox_events_use_case,
    )
