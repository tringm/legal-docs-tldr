import json
import logging
from pathlib import Path
from typing import List, Tuple, Optional

from core.utils.generic_utils import ROOT_PATH
from core.utils.logging_utils import log_exec_time

LOG = logging.getLogger("TosdrDataPreprocessor")


class TosdrDataPreprocessor:
    def __init__(
            self,
            services_data_folder: Path = ROOT_PATH / 'data' / 'tosdr_services',
            load_all_services: bool = True
    ):
        self._services_data_folder = services_data_folder
        self._loaded_services_data = {}
        if load_all_services:
            self.load_all_services_data_in_folder(self._services_data_folder)

    @property
    def loaded_services(self) -> List:
        return list(self._loaded_services_data.keys())

    def get_service_data(self, service_name: str):
        service_data = self._loaded_services_data.get(service_name)
        if not service_data:
            raise ValueError(f'`{service_name}` content not loaded')
        return service_data

    @log_exec_time(LOG)
    def load_service_content_by_path(self, service_file_path: Path, reload=False, service_name: str = None):
        if not service_file_path.exists():
            raise FileNotFoundError(f'{service_file_path} does not exist at')

        if not service_name:
            service_name = service_file_path.stem

        if service_name not in self._loaded_services_data or reload:
            try:
                with service_file_path.open() as f:
                    content = json.load(f)
            except Exception as e:
                LOG.error(f'failed to load `{service_name}` content file {service_file_path}: {e}')
                raise e
            self._loaded_services_data[service_name] = content
        else:
            LOG.info(f'`{service_name}` content existed')

    @log_exec_time(LOG)
    def load_all_services_data_in_folder(self, folder_path: Path):
        LOG.debug(f"loading TosDR services data from {folder_path}...")
        for file_path in folder_path.glob("*.json"):
            try:
                self.load_service_content_by_path(file_path)
                LOG.debug(f"loaded {file_path}")
            except Exception as e:
                LOG.error(f"failed to load file {file_path} : {e}")
                continue
        LOG.info(f"loaded {len(self._loaded_services_data)} tosdr services data file")

    @log_exec_time(LOG)
    def service_quote_text_and_summary(self, service_name) -> List[Tuple[Optional[str], Optional[str]]]:
        """return tuples of quote text and the summary made by tosdr
        """
        service_data = self.get_service_data(service_name)
        service_point_data = service_data.get('pointsData')
        if not service_point_data:
            raise RuntimeError(f'`{service_name}` pointsData content not found')

        return [(point_datum.get('quoteText'), point_datum.get('title')) for point_datum in service_point_data.values()]

    @log_exec_time(LOG)
    def service_urls(self, service_name):
        """return the urls of a service
        """
        service_data = self.get_service_data(service_name)
        return service_data.get('urls')

