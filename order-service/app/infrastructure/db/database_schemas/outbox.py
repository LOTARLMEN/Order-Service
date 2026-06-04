from datetime import datetime
from uuid import UUID, uuid4

from app.core.models import OrderEventType, OutboxEventStatus
from app.infrastructure.db.database_schemas.base import Base
from sqlalchemy import JSON, TEXT, TIMESTAMP, Index, func
from sqlalchemy import UUID as SQL_UUID
from sqlalchemy.orm import Mapped, mapped_column


class Outbox(Base):
    __tablename__ = "outbox_events"

    id: Mapped[UUID] = mapped_column(
        SQL_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    event_type: Mapped[OrderEventType] = mapped_column(
        TEXT,
        nullable=False,
    )
    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
    status: Mapped[OutboxEventStatus] = mapped_column(
        TEXT,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        Index(
            "idx_outbox_status_pending",
            "status",
            postgresql_where=(status == "PENDING"),
        ),
    )
