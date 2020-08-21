import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from core.utils.logging_utils import log_exec_time
from bs4 import BeautifulSoup

LOADER_LOG = logging.getLogger("TosdrDataLoader")
PROCESSOR_LOG = logging.getLogger("TosdrDataProcessor")


class LoadingServiceDataError(Exception):
    def __init__(self, service_name, msg=''):
        super().__init__()
        self._service_name = service_name
        self._message = f"failed to load service {service_name}: {msg}"
        LOADER_LOG.error(msg)

    def __str__(self):
        return self._message


class TosdrDataLoader:
    """Manage tosdr service data files"""
    def __init__(self):
        self._loaded_services_data = {}

    @property
    def loaded_services(self) -> List:
        """List: list of the name of services of which the data has been loaded"""
        return list(self._loaded_services_data.keys())

    @log_exec_time(LOADER_LOG)
    def load_service_data_in_file(self, data_file_path, force_reload=False, service_name=None):
        """load service data in a file

        Args:
            data_file_path (Path): path to the data file
            force_reload (bool): reload the data file even if the service data has been loaded before, defaults to False
            service_name (str, optional): use the specified service name instead of file stem, defaults to None

        Returns:
            Dict: loaded data

        """
        if not service_name:
            service_name = data_file_path.stem

        if not data_file_path.exists():
            raise LoadingServiceDataError(service_name, f'{data_file_path} does not exist')

        if service_name not in self._loaded_services_data or force_reload:
            # TODO: replace this one with proper load method to handle different versions of the TOSDR data file or
            #  checking if the content is valid
            try:
                with data_file_path.open() as f:
                    data = json.load(f)
            except Exception as e:
                raise LoadingServiceDataError(service_name, f'failed to load JSON file {data_file_path}: {e}')
            if not data:
                raise LoadingServiceDataError(service_name, f'service data in {data_file_path} is empty')
            self._loaded_services_data[service_name] = data
            return data
        else:
            LOADER_LOG.debug(f'`{service_name}` data existed')
            return self._loaded_services_data[service_name]

    @log_exec_time(LOADER_LOG)
    def load_all_services_data_in_folder(self, folder_path: Path):
        LOADER_LOG.debug(f"loading TosDR services data from {folder_path}...")
        for file_path in folder_path.glob("**/*.json"):
            try:
                self.load_service_data_in_file(file_path)
                LOADER_LOG.debug(f"loaded {file_path}")
            except Exception as e:
                LOADER_LOG.error(f"failed to load file {file_path} : {e}")
                continue
        LOADER_LOG.info(f"loaded {len(self._loaded_services_data)} tosdr services data file")

    def service_data(self, service_name: str):
        if service_name not in self._loaded_services_data:
            raise ValueError(f'`{service_name}` data not found. Please load the service data first')
        return self._loaded_services_data.get(service_name)


def service_quote_text_and_summary(service_data, remove_html_tags = True):
    """

    Args:
        service_data (Dict): the loaded service data

    Returns:
        List[Tuple[Optional[str], Optional[str]]]: a list of tuples of quote text and the corresponding summary

    """
    service_point_data = service_data.get('pointsData')
    if not service_point_data:
        raise RuntimeError(f'`{service_data}` pointsData not found')

    def get_quote_text(point_datum):
        quote_text = point_datum.get('quoteText')
        if remove_html_tags:
            soup = BeautifulSoup(quote_text, 'lxml')
            quote_text = soup.text
        return quote_text

    return [(get_quote_text(point_datum), point_datum.get('title')) for point_datum in service_point_data.values()]


def service_urls(service_data):
    """

    Args:
        service_data (Dict): the loaded service data

    Returns:
        List[str]: list of urls of a service

    """
    return service_data.get('urls')

