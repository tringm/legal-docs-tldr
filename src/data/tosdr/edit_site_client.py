import asyncio

import backoff
from aiohttp import ClientResponseError, ClientSession
from aiolimiter import AsyncLimiter
from loguru import logger
from requests import codes

from src.data.base_client import BaseAPIClient, BaseAPIOperation

from .html_parser import parse_case_point_rows_from_html
from .models import CasePoint

__all__ = [
    "EditSiteClient",
    "GetCasePointsOp",
]


class GetCasePointsOp(BaseAPIOperation):
    method: str = "GET"


class EditSiteClient(BaseAPIClient):
    base_url = "https://edit.tosdr.org"

    def __init__(self) -> None:
        super().__init__(base_url=self.base_url)
        self.rate_limiter = AsyncLimiter(max_rate=1, time_period=1)

    @staticmethod
    def _build_get_case_points_op(case_id: int) -> GetCasePointsOp:
        return GetCasePointsOp(path=f"/cases/{case_id}")

    @staticmethod
    def _parse_case_points_from_html(html: str, case_id: int) -> list[CasePoint]:
        try:
            rows = parse_case_point_rows_from_html(markup=html)
            return [CasePoint.model_validate({"case_id": case_id, **row}) for row in rows]
        except Exception as e:
            logger.error(f"Failed to parse case {case_id} html: {e}")
            raise

    def get_case_points(self, case_id: int) -> list[CasePoint]:
        resp = self.request(api_op=self._build_get_case_points_op(case_id=case_id))
        return self._parse_case_points_from_html(html=resp.text, case_id=case_id)

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=ClientResponseError,
        max_tries=10,
        giveup=lambda e: e.status != codes.too_many,
    )
    async def async_get_case_points(self, session: ClientSession, case_id: int) -> list[CasePoint]:
        async with self.rate_limiter, self.async_request(
            session=session, api_op=self._build_get_case_points_op(case_id=case_id)
        ) as resp:
            logger.info(f"Getting case with id: {case_id}")
            resp_text = await resp.text()
            return self._parse_case_points_from_html(html=resp_text, case_id=case_id)

    async def async_get_multiple_case_points(self, case_ids: list[int]) -> list[CasePoint]:
        async with ClientSession(raise_for_status=True) as session:
            tasks = (self.async_get_case_points(session=session, case_id=c_id) for c_id in case_ids)

            coro_returns = await asyncio.gather(*tasks, return_exceptions=True)

            case_points = []
            for idx, coro_ret in enumerate(coro_returns):
                if isinstance(coro_ret, Exception):
                    logger.error(f"Failed to query service with id {case_ids[idx]}: {coro_ret}")
                else:
                    case_points += coro_ret
            return case_points
