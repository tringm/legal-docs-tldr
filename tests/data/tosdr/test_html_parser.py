import gzip
from pathlib import Path

import pytest

from src.data.tosdr import parse_case_point_rows_from_html


@pytest.fixture
def example_case_html(resources_dir_path: Path) -> bytes:
    with gzip.open(resources_dir_path / "example_case.html.gz", mode="rb") as f:
        return f.read()


def test_parse_case_point_from_html(example_case_html: bytes) -> None:
    def is_valid_case_point_row(row: dict) -> bool:
        return all(title in row for title in ("Service", "Title", "Status"))

    case_point_rows = list(parse_case_point_rows_from_html(markup=example_case_html))
    assert len(case_point_rows) == 3, "Expect parsed 3 case points"  # noqa: PLR2004
    assert all(is_valid_case_point_row(row=row) for row in case_point_rows)
