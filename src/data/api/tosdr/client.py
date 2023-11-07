from pydantic import BaseModel, Field

from src.data.api.client import BaseAPIClient, BaseAPIOperation, Response

from .models import Service

__all__ = [
    "Client",
]


class GetServiceResponse(BaseModel):
    service: Service = Field(alias="parameters")


class Client(BaseAPIClient):
    base_url = "https://api.tosdr.org"
    get_service_op = BaseAPIOperation(method="GET", path="/service/v2/")

    def __init__(self) -> None:
        super().__init__(base_url=self.base_url)

    def _req_get_service(self, service_id: int) -> Response:
        return self.call_api(api_op=self.get_service_op, params={"id": service_id})

    def get_service(self, service_id: int) -> Service:
        resp = self._req_get_service(service_id=service_id)
        return GetServiceResponse.model_validate(resp.json()).service
