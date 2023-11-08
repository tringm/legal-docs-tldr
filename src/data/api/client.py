from typing import Any

import requests
from aiohttp.client import ClientSession, _RequestContextManager
from pydantic import BaseModel, ValidationError, field_validator
from requests import Response, Session


class BaseAPIOperation(BaseModel):
    path: str
    method: str

    @field_validator("path")
    @classmethod
    def is_valid_path(cls, val: str) -> str:
        if not val.startswith("/"):
            raise ValidationError(f"path must starts with `/`: {val}")
        return val


class BaseAPIClient:
    def __init__(self, base_url: str, default_timeout: float = 10.0) -> None:
        self.base_url = base_url
        self.default_timeout = default_timeout
        self.default_req_params = {"timeout": self.default_timeout}  # enforce ruff S113

    def _build_req_params(self, api_op: None | BaseAPIOperation = None, **kwargs: Any) -> dict[str, Any]:
        req_kwargs = {"method": api_op.method, "url": self.base_url + api_op.path} if api_op else {}
        return {**self.default_req_params, **req_kwargs, **kwargs}

    def request(
        self,
        session: None | Session = None,
        api_op: None | BaseAPIOperation = None,
        raise_for_status: bool = True,
        **kwargs: Any,
    ) -> Response:
        req_kwargs = self._build_req_params(api_op=api_op, **kwargs)
        req_func = session.request if session else requests.request
        resp = req_func(**req_kwargs)
        if raise_for_status:
            resp.raise_for_status()
        return resp

    def async_request(
        self,
        session: ClientSession,
        api_op: None | BaseAPIOperation = None,
        raise_for_status: bool = True,
        **kwargs: Any,
    ) -> _RequestContextManager:
        req_kwargs = self._build_req_params(api_op=api_op, raise_for_status=raise_for_status, **kwargs)
        return session.request(**req_kwargs)
