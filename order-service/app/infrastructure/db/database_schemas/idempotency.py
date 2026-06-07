from datetime import datetime

from sqlalchemy import JSON, TIMESTAMP, func, TEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.database_schemas.base import Base


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    idempotency_key: Mapped[str] = mapped_column(
        TEXT,
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
