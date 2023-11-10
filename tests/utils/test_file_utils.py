from collections.abc import Generator
from pathlib import Path

import pytest

from src.utils.file import read_ndjson_gz_file, write_ndjson_gz_file


@pytest.fixture
def sample_ndjson() -> list[dict]:
    return [{"first": 1}, {"second": 2}]


@pytest.fixture
def sample_output_ndjson_gz_file() -> Generator[Path, None, None]:
    fp = (Path(__file__).parent / "sample.ndjson.gz").resolve()
    yield fp
    fp.unlink()


def test_write_read_ndjson_gz(sample_ndjson: list[dict], sample_output_ndjson_gz_file: Path) -> None:
    write_ndjson_gz_file(data=sample_ndjson, output_file=sample_output_ndjson_gz_file)
    assert sample_output_ndjson_gz_file.exists(), f"Expected file {sample_output_ndjson_gz_file}"
    data = read_ndjson_gz_file(input_path=sample_output_ndjson_gz_file)
    assert sample_ndjson == data, "Expected data read from gz ndjson file to be the same"
