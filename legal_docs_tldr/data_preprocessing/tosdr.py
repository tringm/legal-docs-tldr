import json
import logging
from pathlib import Path
from typing import List, Tuple, Optional

from legal_docs_tldr.utils.generic_utils import ROOT_PATH
from legal_docs_tldr.utils.logging_utils import log_timer_wrapper

LOG = logging.getLogger("TosdrDataPreprocessor")


class TosdrDataPreprocessor:
    def __init__(self, services_data_folder: Path = ROOT_PATH / 'data' / 'tosdr_services'):
        self._services_data_folder = services_data_folder
        self._loaded_services_content = {}

    @log_timer_wrapper(LOG)
    def load_service_content_by_path(self, service_file_path: Path, force_reload=False):
        service_name = service_file_path.stem
        if service_name not in self._loaded_services_content or force_reload:
            if not service_file_path.exists():
                raise FileNotFoundError(f'service `{service_name}` data file does not exist at {service_file_path}')
            try:
                with service_file_path.open() as f:
                    content = json.load(f)
            except Exception as e:
                LOG.error(f'failed to load service `{service_name}` data file {service_file_path}')
                raise e
            self._loaded_services_content[service_name] = content
            return content
        else:
            return self._loaded_services_content[service_name]

    def load_service_content_by_name(self, service_name: str):
        return self.load_service_content_by_path(self._services_data_folder / f'{service_name}.json')

    @log_timer_wrapper(LOG)
    def load_all_services_data(self):
        LOG.debug(f"loading TosDR tosdr_services data from {self._services_data_folder}...")
        for file_path in self._services_data_folder.glob("*.json"):
            try:
                self.load_service_content_by_path(file_path)
            except Exception as e:
                LOG.error(f"failed to load file {file_path} : {e}")
                continue
        LOG.info(f"loaded {len(self._loaded_services_content)} tosdr_services")

    @log_timer_wrapper(LOG)
    def parse_service_quote_text_and_summary(self, service_name) -> List[Tuple[Optional[str], Optional[str]]]:
        service_content = self._loaded_services_content.get(service_name)
        if not service_content:
            raise RuntimeError(f'`{service_name}` content not found')

        service_point_data = service_content.get('pointsData')
        if not service_point_data:
            raise RuntimeError(f'`{service_name}` pointsData content not found')

        return [(point_datum.get('quoteText'), point_datum.get('title')) for point_datum in service_point_data.values()]
