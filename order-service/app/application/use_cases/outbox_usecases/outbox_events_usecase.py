import logging
from app.application.use_cases.base import BaseUseCase
from app.infrastructure.services.kafka.producer.producer import KafkaProducerService
from app.infrastructure.services.kafka.producer.producer_dto import KafkaProducerDTO
from app.infrastructure.unit_of_work import UnitOfWork
from app.config.config import settings

logger = logging.getLogger(__name__)


class OutboxEventsUseCase(BaseUseCase):
    def __init__(self, unit_of_work: UnitOfWork, kafka_producer: KafkaProducerService):
        super().__init__(unit_of_work)
        self._kafka_producer = kafka_producer

    async def __call__(self):
        async with self._unit_of_work() as uow:
            events = await uow.outbox.get_pending_events()
            if not events:
                return

            logger.info("Found %d pending outbox events", len(events))

            for event in events:
                try:
                    logger.info(
                        "Publishing event %s (type: %s) to topic %s",
                        event.id,
                        event.event_type,
                        settings.Kafka.ORDER_EVENTS_TOPIC,
                    )
                    await self._kafka_producer.send_message(
                        KafkaProducerDTO(
                            topic=settings.Kafka.ORDER_EVENTS_TOPIC,
                            msg=event.payload,
                            key=str(event.id),
                        )
                    )
                    await uow.outbox.update(event.id)
                    logger.info("Successfully published and updated event %s", event.id)
                except Exception as e:
                    logger.error(
                        "Failed to publish event %s: %s",
                        event.id,
                        str(e),
                        exc_info=True,
                    )

            await uow.commit()
