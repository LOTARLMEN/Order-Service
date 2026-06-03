from app.infrastructure.services.capashino_services.base import CapashinoBaseHTTPClient

from .notifications_dto import NotificationDTO


class NotificationsServiceClient(CapashinoBaseHTTPClient):
    def __init__(self):
        super().__init__(
            client_name="Notifications Service",
            client_url="/api/notifications",
        )

    async def send_notification(self, notification: NotificationDTO) -> dict:
        json_data = notification.model_dump(mode="json")

        notification_response = await self._send_request(
            method="POST",
            path=self._client_url,
            json_data=json_data,
        )
        return notification_response
