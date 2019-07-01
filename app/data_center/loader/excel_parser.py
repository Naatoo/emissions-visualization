import pandas

from typing import List
from itertools import takewhile

class ExcelFileParser:

    def __init__(self, file_name: str) -> None:
        self.file_name = file_name

    def __get_file(self):
        return pandas.ExcelFile(self.file_name)

    def __get_rows(self):
        data = pandas.read_excel(self.file_name).to_dict('list')
        return ((lon, lat, value) for lon, lat, value in zip(data['lon'], data['lat'], data['value']))

    def parse_data_file(self) -> List[tuple]:
        # TODO other sheets
        rows = self.__get_rows()
        for (lon, lat, value) in rows:
            yield lon, lat, value

    def get_data_for_preview(self, limit: int) -> List[tuple]:
        rows = self.__get_rows()
        return [(index + 1, *row) for index, row in takewhile(lambda row: row[0] < limit, enumerate(rows))]

    @property
    def sheet_names(self):
        file = self.__get_file()
        return file.sheet_names
