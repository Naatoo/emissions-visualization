from abc import ABC, abstractmethod

import pandas

from typing import List
from itertools import takewhile


class GenericParser(ABC):

    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.rows = self._get_rows()

    @abstractmethod
    def _get_file(self):
        """ Method returns file """

    @abstractmethod
    def _get_rows(self):
        """ Method opens file and return list of tuples: (lon, lat, value) """

    def rows_generator(self) -> List[tuple]:
        for (lon, lat, value) in self.rows:
            yield lon, lat, value

    def get_data_for_preview(self, limit: int) -> List[tuple]:
        return [(index + 1, *row) for index, row in takewhile(lambda row: row[0] < limit, enumerate(self.rows))]
