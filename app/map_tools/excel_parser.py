import pandas

from typing import List


class ExcelFileParser:

    def __init__(self, file_name: str, **kwargs: dict) -> None:
        self.file_name = file_name
        self.data = self._parse_data_file(kwargs)

    def __get_file(self):
        file = pandas.ExcelFile(self.file_name)
        return file

    def _parse_data_file(self, chosen_criteria: dict) -> List[tuple]:
        data = []
        fields = 0, 1, 7
        # TODO other sheets
        file = pandas.read_excel(self.file_name, usecols=fields, sheet_name='Pm10', skipinitialspace=True)
        for _, row in file.iterrows():
            data.append([float(x) for x in (row['lon_center'], row['lat_canter'], row['value'])])
        return data

    @property
    def coordinates(self):
        """
        Return all parsed coordinates in
        :return:
        """
        coordinates = [row[:2] for row in self.data]
        return coordinates

    @property
    def sheet_names(self):
        file = self.__get_file()
        return file.sheet_names
