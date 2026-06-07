from uuid import UUID

from pydantic import BaseModel


class NotificationDTO(BaseModel):
    message: str
    reference_id: str | UUID
    idempotency_key: str
