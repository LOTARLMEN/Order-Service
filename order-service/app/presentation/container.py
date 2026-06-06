from dependency_injector import containers, providers

from app.application.container import ApplicationContainer
from app.config.config import settings as pydantic_settings
from app.presentation.outbox_worker import OutboxWorker


class PresentationContainer(containers.DeclarativeContainer):
    settings = providers.Configuration()
    settings.from_dict(pydantic_settings.model_dump())
    application_container = providers.Container[ApplicationContainer](
        ApplicationContainer,
        settings=settings,
    )
    outbox_worker = providers.Singleton(
        OutboxWorker,
        outbox_events_use_case=application_container.outbox_events_use_case,
    )
