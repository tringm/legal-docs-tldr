import gzip
import json
import shutil
from collections.abc import Iterable
from pathlib import Path

import ndjson
from pydantic import BaseModel


def gzip_file(input_path: Path, output_path: None | Path = None, keep: bool = False) -> None:
    if not output_path:
        output_path = input_path.parent / f"{input_path.name}.gz"
    with input_path.open("rb") as f_in, gzip.open(output_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    if not keep:
        input_path.unlink()


def _get_ndjson_file_from_gz_file(ndjson_gz_fp: Path) -> Path:
    if not ndjson_gz_fp.name.endswith(".ndjson.gz"):
        raise ValueError("Output file must end with .ndjson.gz")
    return ndjson_gz_fp.parent / ndjson_gz_fp.stem


def write_ndjson_gz(data: list[dict], output_file: Path) -> None:
    ndjson_file = _get_ndjson_file_from_gz_file(ndjson_gz_fp=output_file)
    with ndjson_file.open("w") as f:
        ndjson.dump(data, f)
    gzip_file(ndjson_file, output_file, keep=False)


def write_pydantic_models_ndjson_gz(
    models: Iterable[BaseModel], output_file: Path, model_dump_conf: None | dict = None
) -> None:
    ndjson_file = _get_ndjson_file_from_gz_file(ndjson_gz_fp=output_file)

    if not model_dump_conf:
        model_dump_conf = {"by_alias": True}
    with ndjson_file.open("w") as f:
        f.writelines(mod.model_dump_json(**model_dump_conf) + "\n" for mod in models)
    gzip_file(ndjson_file, output_file, keep=False)


def read_ndjson_gz(input_path: Path, decoder: str = "utf-8") -> list[dict]:
    input_path = Path(input_path)
    records = []
    with gzip.open(input_path, "rb") as in_f:
        line = in_f.readline()
        while line:
            records.append(json.loads(line.decode(decoder)))
            line = in_f.readline()
    return records
