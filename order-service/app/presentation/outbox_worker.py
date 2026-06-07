import asyncio
import logging
from app.application.use_cases.outbox_usecases.outbox_events_usecase import (
    OutboxEventsUseCase,
)

logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(self, outbox_events_use_case: OutboxEventsUseCase):
        self._use_case = outbox_events_use_case
        self._is_running = False

    async def start(self):
        self._is_running = True
        logger.info("Outbox worker started")
        while self._is_running:
            try:
                await self._use_case()
            except Exception as e:
                logger.error("Error in outbox worker loop: %s", str(e))

            await asyncio.sleep(5)

    async def stop(self):
        self._is_running = False
        logger.info("Outbox worker stopped")
