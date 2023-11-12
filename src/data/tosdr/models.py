from pydantic import AwareDatetime, BaseModel

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


class Point(BaseModel, _TrackingTimestampMixin):
    id: int  # noqa: A003
    title: str
    status: str
    analysis: str
    source: None | str = None
    case_id: None | int = None
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
    rating: None | str = None
