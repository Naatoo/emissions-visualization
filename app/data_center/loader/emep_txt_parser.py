from typing import Generator

from app.data_center.loader.generic_parser import GenericParser


class EmepTxtFileParser(GenericParser):
    def __init__(self, file_name: str) -> None:
        super().__init__(file_name)

    def _get_file(self):
        pass  # TODO implementation

    @staticmethod
    def __check_first_data_row(lines: list) -> int:
        data_row_index = None
        for index, line in enumerate(lines):
            if "#" not in line:
                data_row_index = index
                break
        return data_row_index

    def _get_rows(self) -> Generator[tuple, None, None]:
        data = {}
        with open(self.file_name) as file:
            lines = file.readlines()
            first_data_row = self.__check_first_data_row(lines)
            for line in lines[first_data_row:]:
                line_data = line.strip().split(";")
                data[tuple(float(x) for x in line_data[4:6])] = float(line_data[-1])
        for key, value in data.items():
            yield (*key, value)
