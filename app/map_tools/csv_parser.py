from typing import List


class CSVFileParser:

    def __init__(self, file_name: str, **kwargs: dict) -> None:
        self.file_name = file_name
        self.data = self._parse_data_file(kwargs)

    def _parse_data_file(self, chosen_criteria: dict) -> List[tuple]:
        # country = self.__validate_country_criteria(chosen_criteria)
        data = {}
        with open(self.file_name) as file:
            for line in file.readlines():
                line_data = line.strip().split(";")
                # if chosen_criteria.get("country") == line_data[0]:
                    # (LAT, LON, VALUE)
                data[tuple(float(x) for x in line_data[4:6])] = float(line_data[-1])
        # if not data:
        #     raise ValueError("Unknown country code: {}".format(country))
        final_data = [[*key, value] for key, value in data.items()]
        return final_data


    @property
    def coordinates(self):
        """
        Return all parsed coordinates in
        :return:
        """
        coordinates = [row[:2] for row in self.data]
        return coordinates
