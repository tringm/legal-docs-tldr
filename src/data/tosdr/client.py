import asyncio
from typing import Generic, TypeVar

import aiohttp
import backoff
from aiohttp.client import ClientSession
from aiolimiter import AsyncLimiter
from loguru import logger
from pydantic import BaseModel
from requests import codes

from src.data.base_client import BaseAPIClient, BaseAPIOperation

from .models import (
    Case,
    Service,
    ServiceMetadata,
    ServiceMetadataPage,
)

__all__ = [
    "Client",
    "GetServiceResponse",
    "GetServiceMetadataPageResponse",
]

ResponseModelType = TypeVar("ResponseModelType")


class BaseResponse(BaseModel, Generic[ResponseModelType]):
    parameters: ResponseModelType


class GetServiceResponse(BaseResponse[Service]):
    @property
    def service(self) -> Service:
        return self.parameters


class GetServiceMetadataPageResponse(BaseResponse[ServiceMetadataPage]):
    @property
    def services_metadata(self) -> list[ServiceMetadata]:
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


class GetCaseResponse(BaseResponse[Case]):
    @property
    def case(self) -> Case:
        return self.parameters


class GetServiceOp(BaseAPIOperation):
    method: str = "GET"
    path: str = "/service/v1"


class GetCaseOp(BaseAPIOperation):
    method: str = "GET"
    path: str = "/case/v1"


class Client(BaseAPIClient):
    base_url = "https://api.tosdr.org"

    def __init__(self) -> None:
        super().__init__(base_url=self.base_url)
        self.rate_limiter = AsyncLimiter(max_rate=1, time_period=1.5)

    @staticmethod
    def _build_get_service_op(service_id: int) -> GetServiceOp:
        return GetServiceOp(params={"service": service_id})

    @staticmethod
    def _build_get_service_metadata_op(page_index: int) -> GetServiceOp:
        return GetServiceOp(params={"page": page_index})

    def get_service(self, service_id: int) -> Service:
        resp = self.request(api_op=self._build_get_service_op(service_id=service_id))
        return GetServiceResponse.model_validate(resp.json()).service

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=aiohttp.ClientResponseError,
        max_tries=10,
        giveup=lambda e: e.status != codes.too_many,
    )
    async def async_get_service(self, session: ClientSession, service_id: int) -> Service:
        async with self.rate_limiter, self.async_request(
            session=session, api_op=self._build_get_service_op(service_id=service_id)
        ) as resp:
            logger.info(f"Getting service with id: {service_id}")
            json_resp = await resp.json()
            return GetServiceResponse.model_validate(json_resp).service

    def get_service_metadata_page(self, page_index: int) -> GetServiceMetadataPageResponse:
        resp = self.request(api_op=self._build_get_service_metadata_op(page_index=page_index))
        return GetServiceMetadataPageResponse.model_validate(resp.json())

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=aiohttp.ClientResponseError,
        max_tries=10,
        giveup=lambda e: e.status != codes.too_many,
    )
    async def async_get_services_metadata(self, session: ClientSession, page_index: int) -> list[ServiceMetadata]:
        async with self.rate_limiter, self.async_request(
            session=session, api_op=self._build_get_service_metadata_op(page_index=page_index)
        ) as resp:
            logger.info(f"Getting service page {page_index}")
            json_resp = await resp.json(content_type=None)
            return GetServiceMetadataPageResponse.model_validate(json_resp).services_metadata

    async def async_get_services_metadata_from_pages(self, page_indices: list[int]) -> list[ServiceMetadata]:
        async with ClientSession(raise_for_status=True) as session:
            tasks = (
                self.async_get_services_metadata(session=session, page_index=page_idx) for page_idx in page_indices
            )

            coro_returns = await asyncio.gather(*tasks, return_exceptions=True)

            serv_metadata = []
            for idx, coro_ret in enumerate(coro_returns):
                if isinstance(coro_ret, Exception):
                    logger.error(f"Failed to query service page {page_indices[idx]}: {coro_ret}")
                else:
                    serv_metadata += coro_ret
            return serv_metadata

    def get_all_services_metadata(self) -> list[ServiceMetadata]:
        first_page = self.get_service_metadata_page(page_index=1)
        remaining_pages_indices = list(range(2, first_page.total_page_count + 1))
        remaining_serv_metadata = asyncio.run(
            self.async_get_services_metadata_from_pages(page_indices=remaining_pages_indices)
        )
        return [*first_page.services_metadata, *remaining_serv_metadata]

    async def async_get_services(self, services_ids: list[int]) -> list[Service]:
        async with ClientSession(raise_for_status=True) as session:
            tasks = (self.async_get_service(session=session, service_id=serv_id) for serv_id in services_ids)

            coro_returns = await asyncio.gather(*tasks, return_exceptions=True)

            services = []
            for idx, coro_ret in enumerate(coro_returns):
                if isinstance(coro_ret, Exception):
                    logger.error(f"Failed to query service with id {services_ids[idx]}: {coro_ret}")
                else:
                    services.append(coro_ret)
            return services

    @staticmethod
    def _build_get_case_op(case_id: int) -> GetCaseOp:
        return GetCaseOp(params={"case": case_id})

    def get_case(self, case_id: int) -> Case:
        resp = self.request(api_op=self._build_get_case_op(case_id=case_id))
        return GetCaseResponse.model_validate(resp.json()).case
