from collections.abc import Generator
from pathlib import Path

import pytest
from pydantic import BaseModel

from src.utils.file_utils import read_ndjson_gz, write_ndjson_gz, write_pydantic_models_ndjson_gz


class SampleModel(BaseModel):
    pos: int


@pytest.fixture
def sample_models() -> list[BaseModel]:
    return [SampleModel(pos=1), SampleModel(pos=2)]


@pytest.fixture
def sample_ndjson() -> list[dict]:
    return [{"pos": 1}, {"pos": 2}]


@pytest.fixture
def sample_output_ndjson_gz_file() -> Generator[Path, None, None]:
    fp = (Path(__file__).parent / "sample.ndjson.gz").resolve()
    yield fp
    fp.unlink()


def test_write_ndjson_gz(sample_ndjson: list[dict], sample_output_ndjson_gz_file: Path) -> None:
    write_ndjson_gz(data=sample_ndjson, output_file=sample_output_ndjson_gz_file)
    assert sample_output_ndjson_gz_file.exists(), f"Expected file {sample_output_ndjson_gz_file}"
    data = read_ndjson_gz(input_path=sample_output_ndjson_gz_file)
    assert sample_ndjson == data, "Expected data read from gz ndjson file to be the same"


def test_write_pydantic_models_ndjson_gz(
    sample_models: list[BaseModel], sample_ndjson: list[dict], sample_output_ndjson_gz_file: Path
) -> None:
    write_pydantic_models_ndjson_gz(models=sample_models, output_file=sample_output_ndjson_gz_file)
    assert sample_output_ndjson_gz_file.exists(), f"Expected file {sample_output_ndjson_gz_file}"
    data = read_ndjson_gz(input_path=sample_output_ndjson_gz_file)
    assert sample_ndjson == data, "Expected data read from gz ndjson file to be the same"
