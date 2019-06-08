import pandas

from typing import List


class ExcelFileParser:

    def __init__(self, file_name: str) -> None:
        self.file_name = file_name

    def __get_file(self):
        file = pandas.ExcelFile(self.file_name)
        return file

    def parse_data_file(self) -> List[tuple]:
        # TODO other sheets
        data = pandas.read_excel(self.file_name).to_dict('list')
        for lon, lat, value in zip(data['lon'], data['lat'], data['value']):
            yield lon, lat, value

    @property
    def sheet_names(self):
        file = self.__get_file()
        return file.sheet_names
