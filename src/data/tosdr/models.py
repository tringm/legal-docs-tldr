from pydantic import (
    AwareDatetime,
    BaseModel,
    Field,
)

__all__ = ["Document", "Point", "Service", "ServiceMetadata"]


class _TrackingTimestampMixin:
    created_at: AwareDatetime
    updated_at: AwareDatetime


class Document(BaseModel, _TrackingTimestampMixin):
    id: int  # noqa: A003
    name: str
    url: str
    xpath: None | str = None
    text: None | str = None


class _RatingObject(BaseModel):
    human_rating: str = Field(alias="human")


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
