from collections.abc import Iterator

from aiolimiter import AsyncLimiter

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
        self.rate_limiter = AsyncLimiter(max_rate=1, time_period=0.5)

    @staticmethod
    def _build_get_case_points_op(case_id: int) -> GetCasePointsOp:
        return GetCasePointsOp(path=f"/cases/{case_id}")

    def get_case_points(self, case_id: int) -> Iterator[CasePoint]:
        resp = self.request(api_op=self._build_get_case_points_op(case_id=case_id))
        return (
            CasePoint.model_validate({"case_id": case_id, **row})
            for row in parse_case_point_rows_from_html(markup=resp.text)
        )
