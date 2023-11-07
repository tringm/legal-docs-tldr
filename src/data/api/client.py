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
    def __init__(self, base_url: str, default_timeout: float = 10) -> None:
        self.base_url = base_url
        self.default_timeout = default_timeout
        self.default_req_params = {"timeout": self.default_timeout}  # enforce ruff S113

    def request(self, session: Session | None = None, **kwargs: Any) -> Response:
        kwargs = {**self.default_req_params, **kwargs}
        req_func = session.request if session else requests.request
        return req_func(**kwargs)

    def call_api(self, api_op: BaseAPIOperation, session: Session | None = None, **kwargs: Any) -> Response:
        kwargs = {"session": session, "url": self.base_url + api_op.path, "method": api_op.method, **kwargs}
        return self.request(**kwargs)

    def get(self, session: Session | None = None, **kwargs: Any) -> Response:
        kwargs = {"method": "get", "timeout": self.default_timeout, "session": session, **kwargs}
        return self.request(**kwargs)

    def post(self, session: Session | None = None, **kwargs: Any) -> Response:
        kwargs = {"method": "post", "timeout": self.default_timeout, "session": session, **kwargs}
        return self.request(**kwargs)

    def put(self, session: Session | None = None, **kwargs: Any) -> Response:
        kwargs = {"method": "put", "timeout": self.default_timeout, "session": session, **kwargs}
        return self.request(**kwargs)

    def patch(self, session: Session | None = None, **kwargs: Any) -> Response:
        kwargs = {"method": "patch", "timeout": self.default_timeout, "session": session, **kwargs}
        return self.request(**kwargs)

    def delete(self, session: Session | None = None, **kwargs: Any) -> Response:
        kwargs = {"method": "delete", "timeout": self.default_timeout, "session": session, **kwargs}
        return self.request(**kwargs)

    def async_request(self, session: ClientSession, **kwargs: Any) -> _RequestContextManager:
        kwargs = {**self.default_req_params, **kwargs}
        return session.request(**kwargs)

    def async_call_api(self, api_op: BaseAPIOperation, session: ClientSession, **kwargs: Any) -> _RequestContextManager:
        kwargs = {"session": session, "url": self.base_url + api_op.path, "method": api_op.method, **kwargs}
        return self.async_request(**kwargs)

    async def async_get(self, session: ClientSession, **kwargs: Any) -> _RequestContextManager:
        kwargs = {"method": "get", "timeout": self.default_timeout, "session": session, **kwargs}
        return self.async_request(**kwargs)

    async def async_post(self, session: ClientSession, **kwargs: Any) -> _RequestContextManager:
        kwargs = {"method": "post", "timeout": self.default_timeout, "session": session, **kwargs}
        return self.async_request(**kwargs)

    async def async_put(self, session: ClientSession, **kwargs: Any) -> _RequestContextManager:
        kwargs = {"method": "put", "timeout": self.default_timeout, "session": session, **kwargs}
        return self.async_request(**kwargs)

    async def async_patch(self, session: ClientSession, **kwargs: Any) -> _RequestContextManager:
        kwargs = {"method": "patch", "timeout": self.default_timeout, "session": session, **kwargs}
        return self.async_request(**kwargs)

    async def async_delete(self, session: ClientSession, **kwargs: Any) -> _RequestContextManager:
        kwargs = {"method": "delete", "timeout": self.default_timeout, "session": session, **kwargs}
        return self.async_request(**kwargs)
