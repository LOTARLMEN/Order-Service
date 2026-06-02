from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.models import (
    InboxEvent,
    InboxEventTypeEnum,
)
from app.infrastructure.db.database_schemas.inbox import Inbox as DBInbox
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.inbox.inbox_dto import InboxEventDTO


class InboxRepository(BaseRepository):
    @staticmethod
    def _construct(db_inbox: DBInbox) -> InboxEvent:
        return InboxEvent(
            order_id=db_inbox.order_id,
            event_type=InboxEventTypeEnum(db_inbox.event_type),
            created_at=db_inbox.created_at,
        )

    async def create(self, event: InboxEventDTO) -> InboxEvent:
        stmt = (
            insert(DBInbox)
            .values(
                {
                    "order_id": event.order_id,
                    "event_type": event.event_type,
                }
            )
            .returning(DBInbox)
        )

        inbox_event = (await self._session.execute(stmt)).scalar_one_or_none()
        if not inbox_event:
            raise RuntimeError("Failed to create inbox event: database returned None.")
        return self._construct(inbox_event)

    async def exists(self, event: InboxEventDTO) -> bool:
        stmt = select(DBInbox).where(
            DBInbox.order_id == event.order_id,
            DBInbox.event_type == event.event_type,
        )
        result = (await self._session.execute(stmt)).scalar_one_or_none()
        return result is not None
