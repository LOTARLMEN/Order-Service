from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.core.models import (
    OutboxEvent,
    OutboxEventStatus,
    OutboxEventTypeEnum,
)
from app.infrastructure.db.database_schemas.outbox import Outbox as DBOutbox
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.exeptions import DoesNotExist
from app.infrastructure.db.repositories.outbox.outbox_dto import OutboxEventDTO


class OutboxRepository(BaseRepository):
    @staticmethod
    def _construct(db_outbox: DBOutbox) -> OutboxEvent:
        return OutboxEvent(
            id=db_outbox.id,
            event_type=OutboxEventTypeEnum(db_outbox.event_type),
            payload=db_outbox.payload,
            status=OutboxEventStatus(db_outbox.status),
            created_at=db_outbox.created_at,
        )

    async def create(self, event: OutboxEventDTO) -> OutboxEvent:
        stmt = (
            insert(OutboxEvent)
            .values(
                {
                    "event_type": event.event_type,
                    "payload": event.payload,
                    "status": OutboxEventStatus.PENDING,
                }
            )
            .returning(OutboxEvent)
        )

        outbox_event = (await self._session.execute(stmt)).scalar_one_or_none()
        if not outbox_event:
            raise RuntimeError("Failed to create outbox event: database returned None.")

        return self._construct(outbox_event)

    async def get_pending_events(self, limit: int = 100) -> list[OutboxEvent]:
        stmt = (
            select(DBOutbox)
            .where(DBOutbox.event_type == OutboxEventStatus.PENDING)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        events = (await self._session.execute(stmt)).scalars()
        return [self._construct(event) for event in events]

    async def get_by_id(self, event_id: UUID) -> OutboxEvent:
        stmt = select(OutboxEvent).where(DBOutbox.id == event_id)
        event = (await self._session.execute(stmt)).scalar_one_or_none()
        if not event:
            raise DoesNotExist
        return self._construct(event)

    async def update(self, event_id: UUID):
        stmt = (
            update(DBOutbox)
            .where(DBOutbox.id == event_id)
            .values(status=OutboxEventStatus.SENT)
        )
        await self._session.execute(stmt)
