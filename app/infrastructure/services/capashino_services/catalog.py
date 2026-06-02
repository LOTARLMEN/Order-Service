from urllib.parse import urljoin
from uuid import UUID

from app.core.models import Item

from .base import CapashinoBaseHTTPClient


class CatalogServiceClient(CapashinoBaseHTTPClient):
    def __init__(self) -> None:
        super().__init__(
            client_name="Catalog Service",
            client_url="/api/catalog/items/",
        )

    async def get_item(self, item_id: UUID) -> Item:
        path = urljoin(self._client_url, str(item_id))
        item = await self._send_request(method="GET", path=path)
        return Item(**item)
