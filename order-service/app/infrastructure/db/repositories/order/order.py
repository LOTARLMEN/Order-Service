from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import joinedload

from app.application.use_cases.order_usecases.order_dto import OrderDTO
from app.core.models import (
    Item,
    Order,
    OrderStatusEnum,
    OrderStatusHistory,
)
from app.infrastructure.db.database_schemas.order import Order as DBOrder
from app.infrastructure.db.database_schemas.order import OrderStatus as DBOrderStatus
from app.infrastructure.db.repositories.base import BaseRepository


class OrderRepository(BaseRepository):
    def _construct(self, db_order: DBOrder | None) -> Order | None:
        if not db_order:
            return None

        # Explicitly sort statuses by created_at and id descending to ensure the latest is first
        sorted_db_statuses = sorted(
            db_order.statuses,
            key=lambda s: (s.created_at, s.id),
            reverse=True,
        )

        return Order(
            id=db_order.id,
            user_id=db_order.user_id,
            item=Item(**db_order.item),
            quantity=db_order.quantity,
            status=OrderStatusEnum(sorted_db_statuses[0].status),
            created_at=db_order.created_at,
            status_history=[
                OrderStatusHistory(
                    status=OrderStatusEnum(s.status), created_at=s.created_at
                )
                for s in sorted_db_statuses
            ],
        )

    async def create(self, order: OrderDTO) -> Order | None:
        db_order = DBOrder(
            user_id=order.user_id,
            item=Item(**order.item).model_dump(mode="json"),
            quantity=order.quantity,
        )
        self._session.add(db_order)
        await self._session.flush()

        db_order_status = DBOrderStatus(
            order_id=db_order.id,
            status=order.status,
        )

        self._session.add(db_order_status)
        await self._session.flush()

        order = await self.get_by_id(db_order.id)
        return order

    async def get_by_id(self, order_id: UUID) -> Order | Any:
        stmt = (
            select(DBOrder)
            .where(DBOrder.id == order_id)
            .options(joinedload(DBOrder.statuses))
        )
        order = (await self._session.execute(stmt)).unique().scalar_one_or_none()

        return self._construct(order)

    async def update_status(
        self, order_id: UUID, status: OrderStatusEnum
    ) -> Order | None:
        stmt_update = insert(DBOrderStatus).values(
            {
                "order_id": order_id,
                "status": status,
            }
        )
        await self._session.execute(stmt_update)
        order = await self.get_by_id(order_id)
        return order
