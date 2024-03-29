from typing import Any

from pydantic import (
    AwareDatetime,
    BaseModel,
    Field,
    field_validator,
)

__all__ = [
    "BasePage",
    "Case",
    "CasePage",
    "CasePoint",
    "Document",
    "PageInfo",
    "Point",
    "Service",
    "ServiceMetadata",
    "ServiceMetadataPage",
]


class _TrackingTimestampMixin:
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def convert_v1_timestamp_object(cls, data: Any) -> Any:
        """v1 one API use an object format instead of timestamp"""
        if isinstance(data, dict):
            is_valid_time_obj_format = all(k in data for k in ("timezone", "pgsql", "unix"))
            if is_valid_time_obj_format:
                return data["pgsql"]
        return data


class Document(BaseModel, _TrackingTimestampMixin):
    id: int  # noqa: A003
    name: str
    url: str
    xpath: None | str = None
    text: None | str = None


class _RatingObject(BaseModel):
    human_rating: str = Field(alias="human")


class Case(BaseModel, _TrackingTimestampMixin):
    id: int  # noqa: A003
    title: str
    description: str
    classification: _RatingObject

    @property
    def rating(self) -> str:
        return self.classification.human_rating


class Point(BaseModel, _TrackingTimestampMixin):
    id: int  # noqa: A003
    title: str
    status: str
    analysis: str
    case_id: int
    source: None | str = None
    document_id: None | int = None


class Service(BaseModel, _TrackingTimestampMixin):
    id: int  # noqa: A003
    name: str
    points: list[Point]
    urls: list[str]
    rating: None | str = None
    documents: None | list[Document] = None


class ServiceMetadata(BaseModel, _TrackingTimestampMixin):
    id: int  # noqa: A003
    name: str
    rating_: _RatingObject = Field(alias="rating")

    @property
    def rating(self) -> str:
        return self.rating_.human_rating


class PageInfo(BaseModel):
    total: int
    current: int
    start: int
    end: int


class BasePage(BaseModel):
    page_info: PageInfo = Field(alias="_page")


class ServiceMetadataPage(BasePage):
    services: list[ServiceMetadata]


class CasePage(BasePage):
    cases: list[Case]


class CasePoint(BaseModel):
    case_id: int
    service_name: str = Field(alias="Service")
    quote: str = Field(alias="Title")
    status: str = Field(alias="Status")
