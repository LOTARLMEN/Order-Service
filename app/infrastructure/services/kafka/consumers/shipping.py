import json
from asyncio import CancelledError, create_task, sleep
from uuid import UUID

from aiokafka import AIOKafkaConsumer

from app.application.use_cases.process_shipping_event.exceptions import (
    EventAlreadyExistsException,
    OrderNotExistsException,
)
from app.application.use_cases.process_shipping_event.shipping_event import (
    ProcessShippingEventUseCase,
)
from app.config.config import settings
from app.core.models import InboxEventTypeEnum


class ShippingEventConsumer:
    def __init__(self, process_shipping_event_use_case: ProcessShippingEventUseCase):
        self._use_case = process_shipping_event_use_case
        self._url = settings.Kafka.BOOTSTRAP_SERVERS
        self._topic = "student_system-shipment.events"

        self._group_id = "order_service_shipping_group"
        self._consumer = None
        self._is_running = False
        self._task = None

    async def start(self):
        self._consumer = AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._url,
            group_id=self._group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        await self._consumer.start()
        self._is_running = True

        self._task = create_task(self._listen())

    async def _listen(self):
        try:
            async for msg in self._consumer:
                if not self._is_running:
                    break
                try:
                    payload = json.loads(msg.value.decode("utf-8"))

                    event_type = InboxEventTypeEnum(payload["event_type"])
                    order_id = UUID(payload["order_id"])

                    await self._use_case(
                        order_id=order_id,
                        event_type=event_type,
                    )

                    await self._consumer.commit()

                except (EventAlreadyExistsException, OrderNotExistsException):
                    await self._consumer.commit()
                except Exception:
                    await sleep(5)

        finally:
            self._consumer.stop()

    async def stop(self):
        self._is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except CancelledError:
                pass
