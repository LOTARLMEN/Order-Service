from uuid import UUID

from app.infrastructure.db.database_schemas.idempotency import IdempotencyKey
from app.infrastructure.db.repositories.base import BaseRepository


class IdempotencyKeyRepository(BaseRepository):
    async def create(self, key: UUID):
        entity = IdempotencyKey(idempotency_key=key)
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def set_response(self, key: UUID, response: dict):
        obj = await self._session.get(IdempotencyKey, key)
        if obj:
            obj.response = response
