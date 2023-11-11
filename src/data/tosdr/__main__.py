from pathlib import Path

import click

from src.utils.file_utils import write_pydantic_models_ndjson_gz
from src.utils.paths import DATA_DIR_PATH

from .client import Client

DEFAULT_ALL_SERVICES_METADATA_OUTPUT_FILE = (DATA_DIR_PATH / "tosdr" / "all_services_metadata.ndjson.gz").resolve()


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option(
    "-o",
    "--output-file",
    default=DEFAULT_ALL_SERVICES_METADATA_OUTPUT_FILE,
    type=click.Path(file_okay=True, dir_okay=False, writable=True, path_type=Path),
)
def download_all_services_metadata(output_file: Path) -> None:
    """Download all services metadata and save as ndjson file"""
    client = Client()
    services_metadata = client.get_all_services_metadata()
    write_pydantic_models_ndjson_gz(models=services_metadata, output_file=output_file)


if __name__ == "__main__":
    cli()
