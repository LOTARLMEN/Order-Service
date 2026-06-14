from app.infrastructure.services.capashino_services.base import CapashinoBaseHTTPClient

from app.application.dto.payments import PaymentDTO


class PaymentServiceClient(CapashinoBaseHTTPClient):
    def __init__(self):
        super().__init__(
            client_name="Payments Service",
            client_url="/api/payments",
        )

    async def create_payment(self, payment_dto: PaymentDTO) -> dict:
        json_data = payment_dto.model_dump(mode="json")
        payment_response = await self._send_request(
            method="POST",
            path=self._client_url,
            json_data=json_data,
        )
        return payment_response
