from app.application.use_cases.outbox_usecases.outbox_events_usecase import (
    OutboxEventsUseCase,
)


class OutboxWorker:
    def __init__(self, outbox_events_use_case: OutboxEventsUseCase): ...
