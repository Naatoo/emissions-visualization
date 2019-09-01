import pandas

from typing import Generator

from app.data_center.loader.generic_parser import GenericParser
from app.tools.exceptions import WrongColNamesException


class ExcelFileParser(GenericParser):
    def __init__(self, file_name: str) -> None:
        super().__init__(file_name)

    def _get_file(self):
        return pandas.ExcelFile(self.file_name)

    def _get_rows(self) -> Generator[tuple, None, None]:
        data = pandas.read_excel(self.file_name).to_dict('list')
        if [key for key in data.keys()] != ['lon', 'lat', 'value']:
            raise WrongColNamesException
        yield from zip(data['lon'], data['lat'], data['value'])

    @property
    def sheet_names(self):
        file = self._get_file()
        return file.sheet_names
