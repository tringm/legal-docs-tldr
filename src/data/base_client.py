from abc import ABC
from typing import Any

import requests
from aiohttp.client import ClientSession, _RequestContextManager
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from requests import Response, Session

DEFAULT_TIMEOUT = 10.0


class BaseAPIOperation(BaseModel, ABC):
    model_config = ConfigDict(extra="allow")

    method: str
    path: str
    params: None | dict = None
    headers: None | dict = None
    cookies: None | dict = None
    files: None | dict = None
    json_: None | dict = Field(default=None, alias="json")  # pydantic reserved key
    data: Any = None
    auth: Any = None

    @field_validator("path")
    @classmethod
    def is_valid_path(cls, val: str) -> str:
        if not val.startswith("/"):
            raise ValidationError(f"path must starts with `/`: {val}")
        return val


class BaseAPIClient:
    def __init__(self, base_url: str, default_timeout: float = DEFAULT_TIMEOUT) -> None:
        self.base_url = base_url
        self.default_timeout = default_timeout
        self.default_req_params = {"timeout": self.default_timeout}  # enforce ruff S113

    def _build_req_params(self, api_op: None | BaseAPIOperation = None, **kwargs: Any) -> dict[str, Any]:
        if api_op:
            req_kwargs = api_op.model_dump(exclude_none=True, by_alias=True)
            req_kwargs["url"] = self.base_url + req_kwargs.pop("path")
        else:
            req_kwargs = {}
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
        **kwargs: Any,
    ) -> _RequestContextManager:
        req_kwargs = self._build_req_params(api_op=api_op, **kwargs)
        return session.request(**req_kwargs)
