import gzip
import json
import shutil
from pathlib import Path

import ndjson


def gzip_file(input_path: Path, output_path: None | Path = None, keep: bool = False) -> None:
    if not output_path:
        output_path = input_path.parent / f"{input_path.name}.gz"
    with input_path.open("rb") as f_in, gzip.open(output_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    if not keep:
        input_path.unlink()


def write_ndjson_gz_file(data: list[dict], output_file: Path) -> None:
    if not output_file.name.endswith(".ndjson.gz"):
        raise ValueError("Output file must end with .ndjson.gz")
    ndjson_file = output_file.parent / output_file.stem
    with ndjson_file.open("w") as f:
        ndjson.dump(data, f)
    gzip_file(ndjson_file, output_file, keep=False)


def read_ndjson_gz_file(input_path: Path, decoder: str = "utf-8") -> list[dict]:
    input_path = Path(input_path)
    records = []
    with gzip.open(input_path, "rb") as in_f:
        line = in_f.readline()
        while line:
            records.append(json.loads(line.decode(decoder)))
            line = in_f.readline()
    return records
