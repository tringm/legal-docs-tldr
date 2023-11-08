from typing import Any, overload

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

    @overload
    def request(self, *, session: None = None, api_op: None | BaseAPIOperation = None, **kwargs: Any) -> Response:
        ...

    @overload
    def request(self, *, session: Session, api_op: None | BaseAPIOperation = None, **kwargs: Any) -> Response:
        ...

    @overload
    def request(
        self, *, session: ClientSession, api_op: None | BaseAPIOperation = None, **kwargs: Any
    ) -> _RequestContextManager:
        ...

    def request(
        self,
        *,
        session: None | Session | ClientSession = None,
        api_op: None | BaseAPIOperation = None,
        **kwargs: Any,
    ) -> Response | _RequestContextManager:
        req_kwargs: dict[str, Any] = {"method": api_op.method, "url": self.base_url + api_op.path} if api_op else {}
        req_kwargs = {**self.default_req_params, **req_kwargs, **kwargs}
        req_func = session.request if session else requests.request
        return req_func(**req_kwargs)
