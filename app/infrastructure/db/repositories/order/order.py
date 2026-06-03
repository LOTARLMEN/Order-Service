from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

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
from app.infrastructure.db.repositories.exeptions import DoesNotExist


class OrderRepository(BaseRepository):
    @staticmethod
    def _construct(db_order: DBOrder) -> Order:
        if not db_order:
            raise DoesNotExist

        return Order(
            id=db_order.id,
            user_id=db_order.user_id,
            items=[Item(**item) for item in db_order.items],
            amount=db_order.amount,
            status=OrderStatusEnum(db_order.statuses[0].status),
            status_history=[
                OrderStatusHistory(
                    status=OrderStatusEnum(s.status), created_at=s.created_at
                )
                for s in db_order.statuses
            ],
        )

    async def create(self, order: OrderDTO) -> Order:
        stmt_order = (
            insert(DBOrder)
            .values(
                {
                    "user_id": order.user_id,
                    "items": order.items,
                    "amount": order.amount,
                }
            )
            .returning(DBOrder)
        )

        order_result = (await self._session.execute(stmt_order)).scalar()

        stmt_status = insert(DBOrderStatus).values(
            {
                "user_id": order_result.id,
                "status": order.status,
            }
        )

        await self._session.execute(stmt_status)

        order = await self.get_by_id(order_result.id)
        return self._construct(order)

    async def get_by_id(self, order_id: UUID) -> Order:
        stmt = select(DBOrder).where(DBOrder.id == order_id)
        order = (await self._session.execute(stmt)).scalar_one_or_none()

        if order is None:
            raise ValueError(f"Order with id {order_id} not found")

        return self._construct(order)

    async def update_status(self, order_id: UUID, status: OrderStatusEnum) -> None:
        stmt_update = insert(DBOrderStatus).values(
            {
                "user_id": order_id,
                "status": status,
            }
        )
        await self._session.execute(stmt_update)
