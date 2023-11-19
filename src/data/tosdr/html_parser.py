from collections.abc import Iterator
from typing import IO, Any

from bs4 import BeautifulSoup, Tag

__all__ = [
    "MarkupType",
    "TagNotFoundException",
    "parse_case_point_rows_from_html",
]

MarkupType = str | bytes | IO[str] | IO[bytes]


class TagNotFoundException(Exception):
    def __init__(self, tag: Tag, tag_name: str):
        self.tag = tag
        self.tag_name = tag_name

    def __str__(self) -> str:
        return f"<{self.tag_name}> not found in {self.tag}"


def _tag_find(tag: Tag, **kwargs: Any) -> Tag:
    res = tag.find(**kwargs)
    if not res:
        raise TagNotFoundException(tag=tag, tag_name=kwargs["name"])
    return res  # type: ignore[return-value]


def _tag_find_all(tag: Tag, **kwargs: Any) -> list[Tag]:
    res = tag.find_all(**kwargs)
    if not res:
        raise TagNotFoundException(tag=tag, tag_name=kwargs["name"])
    return res


def _parse_table_headers(table: Tag) -> list[str]:
    header_group_tag = _tag_find(tag=table, name="thead")
    headers_tag = _tag_find_all(tag=header_group_tag, name="th")
    return [h_tag.text for h_tag in headers_tag]


def _parse_table_row(row: Tag) -> Iterator[str]:
    cells = _tag_find_all(row, name=("th", "td"))
    return (c.text for c in cells)


def _parse_table(table: Tag) -> Iterator[dict]:
    headers = _parse_table_headers(table=table)

    body_tag = _tag_find(tag=table, name="tbody")
    all_rows = (_parse_table_row(row=row) for row in _tag_find_all(tag=body_tag, name="tr"))
    return (dict(zip(headers, row, strict=True)) for row in all_rows)


def parse_case_point_rows_from_html(markup: MarkupType) -> Iterator[dict]:
    page = BeautifulSoup(markup=markup, features="lxml")
    table = _tag_find(tag=page, name="table")
    return _parse_table(table=table)
