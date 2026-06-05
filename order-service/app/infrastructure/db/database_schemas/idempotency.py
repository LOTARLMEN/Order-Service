from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, TIMESTAMP, func
from sqlalchemy import UUID as SQL_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.database_schemas.base import Base


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    idempotency_key: Mapped[UUID] = mapped_column(
        SQL_UUID(as_uuid=True),
        primary_key=True,
    )

    response: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
