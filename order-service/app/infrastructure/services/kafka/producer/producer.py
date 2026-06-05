import json

from aiokafka import AIOKafkaProducer

from app.infrastructure.services.kafka.producer.producer_dto import (
    KafkaProducerDTO,
)


class KafkaProducerService:
    def __init__(self, url: str):
        self._url = url
        self._producer = None

    async def start(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._url,
            value_serializer=lambda m: json.dumps(m).encode("utf-8"),
            enable_idempotence=True,
        )
        await self._producer.start()

    async def stop(self):
        if self._producer:
            await self._producer.stop()

    async def send_message(self, producer_dto: KafkaProducerDTO):
        if not self._producer:
            raise RuntimeError("Producer not started.")

        key_bytes = producer_dto.key.encode("utf-8") if producer_dto.key else None

        await self._producer.send_and_wait(
            topic=producer_dto.topic,
            value=producer_dto.msg,
            key=key_bytes,
        )
