from typing import List


class CSVFileParser:

    def __init__(self, file_name: str) -> None:
        self.file_name = file_name

    def parse_data_file(self) -> List[tuple]:
        data = {}
        with open(self.file_name) as file:
            for line in file.readlines():
                line_data = line.strip().split(";")
                data[tuple(float(x) for x in line_data[4:6])] = float(line_data[-1])
        for key, value in data.items():
            yield (*key, value)
