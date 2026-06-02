from datetime import datetime
from uuid import UUID

from sqlalchemy import TEXT, TIMESTAMP, func
from sqlalchemy import UUID as SQL_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.database_schemas.base import Base


class Inbox(Base):
    __tablename__ = "inbox_events"

    order_id: Mapped[UUID] = mapped_column(
        SQL_UUID(as_uuid=True),
        primary_key=True,
    )
    event_type: Mapped[str] = mapped_column(
        TEXT,
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
