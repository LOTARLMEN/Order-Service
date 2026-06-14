from uuid import UUID

from pydantic import BaseModel


class NotificationDTO(BaseModel):
    user_id: str | UUID
    message: str
    reference_id: str | UUID
    idempotency_key: str
