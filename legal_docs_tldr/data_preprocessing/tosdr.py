import json
import logging
from pathlib import Path
from typing import List, Tuple


class TosdrDataPreprocessor:
    def __init__(self, services_data_folder: Path):
        self.logger = logging.getLogger("TosdrDataPreprocessor")
        self.logger.info(f"Parsing TosDR services data from {services_data_folder}")
        self.services_tosdr = {}
        for file in services_data_folder.glob("*.json"):
            with file.open() as f:
                try:
                    file_content = json.load(f)
                except Exception as e:
                    self.logger.error(f"failed to parse file {file} : {e}")
                    continue
            self.services_tosdr[file.stem] = file_content
        self.logger.info(f"Discovered {len(self.services_tosdr)} services")

    def parse_quote_text_and_summary(self, specific_service: str = None) -> List[Tuple[str, str]]:
        """
        Return tuples of quote text and the summary
        If no specific service is given return all services quote text and summary
        """
        def parse_points_data(points_data):
            return [(point_datum['quoteText'], point_datum['title']) for point_datum in points_data.values()
                    if point_datum.get('quoteText') and point_datum.get('title')]

        if specific_service:
            if specific_service not in self.services_tosdr:
                raise ValueError(f"Service {specific_service} not found")
            return parse_points_data(self.services_tosdr[specific_service]['pointsData'])

        return [parsed
                for service_data in self.services_tosdr.values()
                for parsed in parse_points_data(service_data['pointsData'])]