import json
import logging
from asyncio import CancelledError, create_task, sleep
from uuid import UUID

from aiokafka import AIOKafkaConsumer
from app.application.use_cases.exceptions import (
    EventAlreadyExistsException,
    OrderNotExistsException,
)
from app.application.use_cases.process_shipping_event.shipping_event import (
    ProcessShippingEventUseCase,
)
from app.core.models import OrderEventType

logger = logging.getLogger(__name__)


class ShippingEventConsumer:
    def __init__(
        self,
        process_shipping_event_use_case: ProcessShippingEventUseCase,
        url: str,
    ):
        self._use_case = process_shipping_event_use_case
        self._url = url
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
        logger.info("ShippingEventConsumer started.")

    async def _listen(self):
        try:
            while self._is_running:
                res = await self._consumer.getmany(timeout_ms=1000)

                for topic_partition, messages in res.item():
                    for msg in messages:
                        if not self._is_running:
                            break
                        await self._process_message(msg)

        except CancelledError:
            logger.info("ShippingEventConsumer cancelled")
        except Exception as e:
            logger.error("Unexpected error in consumer loop: {}".format(e))
        finally:
            logger.info("ShippingEventConsumer finished.")
            await self._consumer.stop()

    async def _process_message(self, msg):
        try:
            try:
                payload = json.loads(msg.value.decode("utf-8"))
                event_type = OrderEventType(payload["event_type"])
                order_id = UUID(payload["order_id"])
            except (ValueError, KeyError, TypeError) as parse_err:
                logger.error(
                    "Invalid message structure: {}. Skipping.".format(parse_err)
                )
                await self._consumer.commit()
                return

            try:
                await self._use_case(
                    order_id=order_id,
                    event_type=event_type,
                )
                await self._consumer.commit()

            except (EventAlreadyExistsException, OrderNotExistsException) as biz_err:
                logger.warning(
                    "Business exception: {}. Commiting offset.".format(biz_err)
                )
                await self._consumer.commit()

        except Exception as e:
            logger.error("Unexpected error in consumer loop: {}".format(e))
            await sleep(5)

    async def stop(self):
        logger.info("ShippingEventConsumer stopped.")
        self._is_running = False

        if self._task:
            for _ in range(30):
                if self._task.done():
                    break
                await sleep(0.1)

            if not self._task.done():
                logger.warning("Forcing consumer task cancellation.")
                self._task.cancel()

            try:
                await self._task
            except CancelledError:
                pass
        logger.info("ShippingEventConsumer stopped.")
