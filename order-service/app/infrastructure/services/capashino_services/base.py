from typing import Any

from httpx import AsyncClient, ConnectTimeout, HTTPStatusError, Timeout

from app.config.config import settings
from app.infrastructure.services.exceptions import ProviderError, ProviderTimeout


class CapashinoBaseHTTPClient:
    def __init__(self, client_name: str, client_url: str):
        self.__x_api_key = settings.Capashino.X_API_KEY
        self.__base_url = settings.Capashino.BASE_URL
        self._client_url = client_url
        self._client_name = client_name
        self._client = AsyncClient(
            base_url=self.__base_url,
            headers={"X-API-KEY": self.__x_api_key},
            follow_redirects=True,
            timeout=Timeout(10.0, connect=5),
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _send_request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json_data: dict | None = None,
    ) -> Any:
        try:
            response = await self._client.request(
                method=method,
                url=path,
                params=params,
                json=json_data,
            )

            response.raise_for_status()
            return response.json()

        except ConnectTimeout:
            raise ProviderTimeout(f"Service {self._client_name} timed out.")
        except HTTPStatusError as e:
            raise ProviderError(
                f"Service {self._client_name} failed. Status: {e.response.status_code}, Details: {e.response.text}"
            )
