from uuid import UUID

from pydantic import BaseModel


class InboxEventDTO(BaseModel):
    order_id: UUID
    event_type: str
