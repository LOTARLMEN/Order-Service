from sqlalchemy.exc import IntegrityError

from app.infrastructure.db.database_schemas.idempotency import IdempotencyKey
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.idempotency_key.exceptions import (
    IdempotencyKeyAlreadyExistsError,
)


class IdempotencyKeyRepository(BaseRepository):
    async def create(self, key: str):
        try:
            entity = IdempotencyKey(idempotency_key=key)
            self._session.add(entity)
            await self._session.flush()
            return entity
        except IntegrityError:
            raise IdempotencyKeyAlreadyExistsError

    async def get(self, key: str) -> IdempotencyKey | None:
        return await self._session.get(IdempotencyKey, key)

    async def set_response(self, key: str, response: dict):
        obj = await self.get(key)
        if obj:
            obj.response =