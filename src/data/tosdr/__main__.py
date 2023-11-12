import asyncio
from pathlib import Path

import click
from loguru import logger

from src.data.tosdr import ServiceMetadata
from src.utils.file_utils import read_ndjson_gz, write_pydantic_models_ndjson_gz
from src.utils.paths import DATA_DIR_PATH

from .client import Client

TOSDR_DATA_DIR = (DATA_DIR_PATH / "tosdr").resolve()
DEFAULT_ALL_SERVICES_METADATA_OUTPUT_FILE = TOSDR_DATA_DIR / "all_services_metadata.ndjson.gz"
DEFAULT_ALL_SERVICES_OUTPUT_FILE = TOSDR_DATA_DIR / "all_services.ndjson.gz"


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
    """Download all services metadata and save as gzipped ndjson file"""
    client = Client()
    services_metadata = client.get_all_services_metadata()
    write_pydantic_models_ndjson_gz(models=services_metadata, output_file=output_file)


@cli.command()
@click.option(
    "--metadata-file",
    default=DEFAULT_ALL_SERVICES_METADATA_OUTPUT_FILE,
    type=click.Path(file_okay=True, dir_okay=False, writable=True, path_type=Path),
)
@click.option(
    "-o",
    "--output-file",
    default=DEFAULT_ALL_SERVICES_OUTPUT_FILE,
    type=click.Path(file_okay=True, dir_okay=False, writable=True, path_type=Path),
)
def download_all_services(metadata_file: Path, output_file: Path) -> None:
    """Download all services save as gzipped ndjson file"""
    services_metadata = read_ndjson_gz(input_path=metadata_file)
    services_ids = [ServiceMetadata.model_validate(serv).id for serv in services_metadata]

    logger.info(f"Downloading {len(services_ids)} services")
    client = Client()
    services = asyncio.run(client.async_get_services(services_ids=services_ids))
    write_pydantic_models_ndjson_gz(models=services, output_file=output_file)


if __name__ == "__main__":
    cli()
