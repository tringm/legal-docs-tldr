import pickle
from pathlib import Path

import click

from .client import Client

DEFAULT_ALL_SERVICES_OUTPUT_FILE = "./data/tosdr/all_services.pkl"


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option(
    '-o',
    '--output-file',
    default=DEFAULT_ALL_SERVICES_OUTPUT_FILE,
    type=click.Path(file_okay=True, dir_okay=False, writable=True, path_type=Path)
)
def download_all_services(output_file: Path) -> None:
    """
    Download and save as pickled list[Service]
    """
    client = Client()
    services = client.get_all_services()
    with output_file.open(mode="wb") as f:
        pickle.dump(services, f)


if __name__ == '__main__':
    cli()
