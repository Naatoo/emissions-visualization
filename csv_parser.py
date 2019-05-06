from typing import List


class CSVFileParser:

    def __init__(self, file_name: str, **kwargs: dict) -> None:
        self.file_name = file_name
        self.data = self._parse_data_file(kwargs)

    def _parse_data_file(self, chosen_criteria: dict) -> List[tuple]:
        country = self.__validate_country_criteria(chosen_criteria)
        data = []
        with open(self.file_name) as file:
            for line in file.readlines():
                line_data = line.strip().split(";")
                if chosen_criteria.get("country") == line_data[0]:
                    # (LAT, LON, VALUE)
                    data.append([float(x) for x in (*line_data[4:6], line_data[-1])])
        if not data:
            raise ValueError("Unknown country code: {}".format(country))
        return data

    @staticmethod
    def __validate_country_criteria(user_criteria: dict) -> str:
        country_code = user_criteria.get("country", "")
        if len(country_code) == 2 and (letter.isupper() for letter in country_code):
            country = country_code
        else:
            raise ValueError("Wrong country code format: {}".format(country_code))
        # TODO lat, lon
        return country


    @property
    def coordinates(self):
        """
        Return all parsed coordinates in
        :return:
        """
        coordinates = [row[:2] for row in self.data]
        return coordinates
