import logging

from app.application.use_cases.base import BaseUseCase
from app.config.config import settings
from app.core.models import OrderEventType
from app.infrastructure.services.capashino_services.notifications.notifications import (
    NotificationsServiceClient,
)
from app.infrastructure.services.capashino_services.notifications.notifications_dto import (
    NotificationDTO,
)
from app.infrastructure.services.kafka.producer.producer import KafkaProducerService
from app.infrastructure.services.kafka.producer.producer_dto import KafkaProducerDTO
from app.infrastructure.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class OutboxEventsUseCase(BaseUseCase):
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        kafka_producer: KafkaProducerService,
        notification_service: NotificationsServiceClient,
    ):
        super().__init__(unit_of_work)
        self._kafka_producer = kafka_producer
        self._notification_service = notification_service

    async def __call__(self):
        async with self._unit_of_work() as uow:
            events = await uow.outbox.get_pending_events()
            if not events:
                return

            logger.info("Found %d pending outbox events", len(events))

            for event in events:
                try:
                    if event.event_type == OrderEventType.NOTIFICATION_SEND:
                        logger.info("Sending notification for event %s", event.id)
                        await self._notification_service.send_notification(
                            NotificationDTO.model_validate(event.payload)
                        )
                    else:
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
                    logger.info("Successfully processed and updated event %s", event.id)
                except Exception as e:
                    logger.error("Failed to process event %s: %s", event.id, str(e))

            await uow.commit()
