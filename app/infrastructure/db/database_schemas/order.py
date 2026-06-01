from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    DECIMAL,
    INTEGER,
    JSON,
    TEXT,
    TIMESTAMP,
    ForeignKey,
    func,
)
from sqlalchemy import UUID as SQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(
        SQL_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
    )
    user_id: Mapped[str] = mapped_column(
        nullable=False,
    )
    items: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
    statuses: Mapped[list["OrderStatus"]] = relationship(
        "OrderStatus",
        back_populates="order",
        order_by="OrderStatus.created_at.desc()",
    )


class OrderStatus(Base):
    __tablename__ = "order_statuses"

    id: Mapped[int] = mapped_column(
        INTEGER,
        primary_key=True,
    )
    order_id: Mapped[UUID] = mapped_column(
        SQL_UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
    )
    status: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="statuses",
    )
