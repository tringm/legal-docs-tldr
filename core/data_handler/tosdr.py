import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

from core.utils.logging_utils import log_exec_time
from bs4 import BeautifulSoup

LOADER_LOG = logging.getLogger("TosdrDataLoader")
PROCESSOR_LOG = logging.getLogger("TosdrDataProcessor")


class ServiceDataLoadError(Exception):
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
        # TODO: Store file path and not load all services into memory
        self._all_service_data = {}

    def add_service_data(self, service_name: str, service_data: 'TosdrServiceData', force_reload=False):
        """ Add a service data

        Args:
            service_name (str): name of the service
            service_data (TosdrServiceData): service data
            force_reload (bool, optional): reload the data file even if the service data has been loaded before, defaults to False

        Returns:

        """
        if service_name in self._all_service_data and not force_reload:
            LOADER_LOG.debug(f"{service_name} data existed and not force reload")
        else:
            self._all_service_data[service_name] = service_data

    @property
    def loaded_services(self) -> List:
        """List: list of the name of services of which the data has been loaded"""
        return list(self._all_service_data.keys())

    def load_service_data_from_file(self, data_file_path, service_name=None, force_reload=False):
        """load service data in a file

        Args:
            data_file_path (Path): path to the data file
            service_name (str, optional): use the specified service name instead of file stem, defaults to None
            force_reload (bool, optional): reload the data file even if the service data has been loaded before, defaults to False

        Returns:
            TosdrServiceData: loaded service data

        """
        if not service_name:
            service_name = data_file_path.stem

        if not data_file_path.exists():
            raise ServiceDataLoadError(service_name, f'{data_file_path} does not exist')

        if service_name not in self._all_service_data or force_reload:
            try:
                with data_file_path.open() as f:
                    json_content = json.load(f)
            except Exception as e:
                raise ServiceDataLoadError(service_name, f'failed to load JSON file {data_file_path}: {e}')
            if not json_content:
                raise ServiceDataLoadError(service_name, f'service data in {data_file_path} is empty')
            service_data = TosdrServiceData.from_tosdr_data_file_json_content(service_name, json_content)
            self.add_service_data(service_name, service_data, force_reload)
            return service_data
        else:
            LOADER_LOG.debug(f'`{service_name}` data existed and not force reload')
            return self._all_service_data[service_name]

    @log_exec_time(LOADER_LOG)
    def load_all_services_file_in_folder(self, data_folder: Path):
        if not data_folder.exists():
            raise FileExistsError(f"service data folder {data_folder} not found")
        LOADER_LOG.debug(f"loading TosDR services data from {data_folder}...")
        for file_path in data_folder.glob("**/*.json"):
            try:
                self.load_service_data_from_file(file_path)
                LOADER_LOG.debug(f"loaded {file_path}")
            except Exception as e:
                LOADER_LOG.error(f"failed to load file {file_path} : {e}")
                continue
        LOADER_LOG.info(f"loaded {len(self._all_service_data)} tosdr services data file")

    def service_data(self, service_name: str) -> 'TosdrServiceData':
        if service_name not in self._all_service_data:
            raise ValueError(f'`{service_name}` data not found. Please load the service data first')
        return self._all_service_data[service_name]


@dataclass
class TosdrServiceSummaryCase:
    """Data class for a tosdr service `pointsData` but only for cases that summarize a quoted text

    Args:
        point_id (str): the id of the point
        quote_document (str): the name of the document of the service that was quoted
        quote_text (str): the quoted text of the document
        summary (str): the tosdr summary (`tosdr.case` by default, `title` if case does not exist)
        point (str): the severity (neutral, bad, good)
    """
    point_id: str
    quote_document: str
    quote_text: str
    summary: str
    rating: str

    @classmethod
    def from_tosdr_point_data(cls, point_data):
        quote_doc = point_data.get('quoteDoc')
        if not quote_doc:
            raise KeyError('`quoteDoc` field not found, point data is not a summary case')
        # remove html tag in quote text
        quote_text = BeautifulSoup(point_data['quoteText'], 'lxml').text
        return cls(
            point_data['id'],
            quote_doc,
            quote_text,
            point_data['tosdr']['case'],
            point_data['tosdr']['point']
        )


@dataclass
class TosdrServiceData:
    """Data class for tosdr service data from tosdr.org API

    Args:
        service_name (str): the name of the service
        documents (List[str]): list of documents of a service
        summary_cases (List[TosdrServiceSummaryCase): list of summary data
    """
    service_name: str
    documents: List[str]
    summary_cases: List[TosdrServiceSummaryCase]

    @classmethod
    def from_tosdr_data_file_json_content(cls, service_name, json_content):
        points_data = json_content.get('pointsData')
        if not points_data:
            raise ServiceDataLoadError('the service has no pointsData')

        summary_cases = []
        for case in points_data.values():
            try:
                case = TosdrServiceSummaryCase.from_tosdr_point_data(case)
                summary_cases.append(case)
            except Exception as e:
                LOADER_LOG.error(f"failed to load {service_name} point data {case['id']}: {e}")

        # Not using the `links` field since it's often missing and not updated
        documents = list({case.quote_document for case in summary_cases})
        return cls(service_name, documents, summary_cases)

    @property
    def all_quote_texts_and_summaries(self) -> List[Tuple[str, str]]:
        """

        Returns:
            List[Tuple[str, str]]: a list of tuples of quote text and the corresponding summary
        """
        return [(case.quote_text, case.summary) for case in self.summary_cases]