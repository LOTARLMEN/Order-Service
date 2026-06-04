from contextlib import asynccontextmanager

from app.infrastructure.db.repositories.inbox.inbox import InboxRepository
from app.infrastructure.db.repositories.order.order import OrderRepository
from app.infrastructure.db.repositories.outbox.outbox import OutboxRepository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class UnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self._session = None

    @asynccontextmanager
    async def __call__(self):
        async with self._session_factory() as session:
            try:
                yield _UnitOfWorkImplementation(session)
                await session.rollback()
            except Exception:
                await session.rollback()
                raise


class _UnitOfWorkImplementation:
    def __init__(self, session: AsyncSession):
        self._session = session

        self._order_repo = OrderRepository(session)
        self._outbox_repo = OutboxRepository(session)
        self._inbox_repo = InboxRepository(session)

    @property
    def orders(self):
        return self._order_repo

    @property
    def outbox(self):
        return self._outbox_repo

    @property
    def inbox(self):
        return self._inbox_repo

    async def commit(self):
        await self._session.commit()
