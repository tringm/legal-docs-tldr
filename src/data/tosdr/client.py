import asyncio

import aiohttp
import backoff
from aiohttp.client import ClientSession
from aiolimiter import AsyncLimiter
from loguru import logger
from pydantic import BaseModel, Field
from requests import codes

from src.data.base_client import BaseAPIClient, BaseAPIOperation, Response

from .models import Service

__all__ = [
    "Client",
    "GetServiceResponse",
    "GetServicePageResponse",
]


class GetServiceResponse(BaseModel):
    service: Service = Field(alias="parameters")


class GetServicePageResponse(BaseModel):
    class _Parameter(BaseModel):
        class PageInfo(BaseModel):
            total: int  # total number of service
            current: int  # current page
            start: int
            end: int

        page_info: PageInfo = Field(alias="_page")
        services: list[Service]

    parameters: _Parameter

    @property
    def services(self) -> list[Service]:
        return self.parameters.services

    @property
    def total_service_count(self) -> int:
        return self.parameters.page_info.total

    @property
    def total_page_count(self) -> int:
        return self.parameters.page_info.end

    @property
    def current_page(self) -> int:
        return self.parameters.page_info.current


class Client(BaseAPIClient):
    base_url = "https://api.tosdr.org"
    get_service_op = BaseAPIOperation(method="GET", path="/service/v2/")

    def __init__(self) -> None:
        super().__init__(base_url=self.base_url)
        self.rate_limieter = AsyncLimiter(max_rate=1, time_period=1.5)

    def _req_get_service(self, service_id: int) -> Response:
        return self.request(api_op=self.get_service_op, params={"id": service_id})

    def get_service(self, service_id: int) -> Service:
        resp = self._req_get_service(service_id=service_id)
        return GetServiceResponse.model_validate(resp.json()).service

    def get_service_page(self, page: None | int = 1) -> GetServicePageResponse:
        resp = self.request(api_op=self.get_service_op, params={"page": page})
        return GetServicePageResponse.model_validate(resp.json())

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=aiohttp.ClientResponseError,
        max_tries=10,
        giveup=lambda e: e.status != codes["too_many"],
    )
    async def _async_get_services_by_page(self, session: ClientSession, page: int) -> list[Service]:
        async with self.rate_limieter, self.async_request(
            session=session, api_op=self.get_service_op, params={"page": page}, raise_for_status=True
        ) as resp:
            logger.info(f"Getting service page {page}")
            _json_resp = await resp.json(content_type=None)
            return GetServicePageResponse.model_validate(_json_resp).services

    async def _async_get_services(self, page_indexes: list[int]) -> list[Service]:
        async with ClientSession(raise_for_status=True) as session:
            tasks = (self._async_get_services_by_page(session=session, page=page) for page in page_indexes)

            coro_returns = await asyncio.gather(*tasks, return_exceptions=True)

            services = []
            for idx, coro_ret in enumerate(coro_returns):
                if isinstance(coro_ret, Exception):
                    logger.error(f"Failed to query service page {page_indexes[idx]}: {coro_ret}")
                else:
                    services += coro_ret
            return services

    def get_all_services(self) -> list[Service]:
        first_page = self.get_service_page(page=1)
        remaining_pages_services = asyncio.run(
            self._async_get_services(
                page_indexes=list(range(2, first_page.total_page_count + 1)),
            )
        )
        return [*first_page.services, *remaining_pages_services]
