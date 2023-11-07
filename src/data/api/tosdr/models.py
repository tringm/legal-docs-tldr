from pydantic import AwareDatetime, BaseModel

__all__ = ["Document", "Point", "Service"]


class _TrackingTimestampMixin:
    created_at: AwareDatetime
    updated_at: AwareDatetime


class Document(BaseModel, _TrackingTimestampMixin):
    id: int  # noqa: A003
    name: str
    url: str
    xpath: None | str = None
    text: None | str = None


class Point(BaseModel, _TrackingTimestampMixin):
    id: int  # noqa: A003
    title: str
    source: str
    status: str
    analysis: str
    case_id: None | int = None
    document_id: None | int = None


class Service(BaseModel):
    id: int  # noqa: A003
    name: str
    rating: str
    urls: list[str]
    documents: list[Document]
    points: list[Point]
