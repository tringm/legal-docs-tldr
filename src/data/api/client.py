from typing import Any

import requests
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

    def request(self, session: Session | None = None, **kwargs: Any) -> Response:
        kwargs = {"timeout": self.default_timeout, **kwargs}  # enforce ruff S113
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
