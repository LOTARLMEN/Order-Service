from uuid import UUID

from sqlalchemy import select, update

from app.application.use_cases.outbox_usecases.outbox_dto import OutboxEventDTO
from app.core.models import (
    OrderEventType,
    OutboxEvent,
    OutboxEventStatus,
)
from app.infrastructure.db.database_schemas.outbox import Outbox as DBOutbox
from app.infrastructure.db.repositories.base import BaseRepository


class OutboxRepository(BaseRepository):
    @staticmethod
    def _construct(db_outbox: DBOutbox | None) -> OutboxEvent | None:
        if not db_outbox:
            return None
        return OutboxEvent(
            id=db_outbox.id,
            event_type=OrderEventType(db_outbox.event_type),
            payload=db_outbox.payload,
            status=OutboxEventStatus(db_outbox.status),
            created_at=db_outbox.created_at,
        )

    async def create(self, event: OutboxEventDTO) -> OutboxEvent | None:
        db_outbox_event = DBOutbox(
            event_type=event.event_type,
            payload=event.payload,
            status=event.status,
        )
        self._session.add(db_outbox_event)
        await self._session.flush()
        return self._construct(db_outbox_event)

    async def get_pending_events(self, limit: int = 100) -> list[OutboxEvent | None]:
        stmt = (
            select(DBOutbox)
            .where(DBOutbox.event_type == OutboxEventStatus.PENDING)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        events = (await self._session.execute(stmt)).scalars()
        return [self._construct(event) for event in events]

    async def get_by_id(self, event_id: UUID) -> OutboxEvent | None:
        stmt = select(DBOutbox).where(DBOutbox.id == event_id)
        event = (await self._session.execute(stmt)).scalar_one_or_none()
        return self._construct(event)

    async def update(self, event_id: UUID):
        stmt = (
            update(DBOutbox)
            .where(DBOutbox.id == event_id)
            .values(status=OutboxEventStatus.SENT)
        )
        await self._session.execute(stmt)
