import numpy as np
import scipy.ndimage as ndimage

from typing import List

from app.tools.paths import BOUNDING_BOXES_JSON
import json
from decimal import Decimal


class Interpolator:

    def __init__(self, raw_data: List[tuple], grid_resolution, boundary_values=None, country_code=None) -> None:
        self.raw_data = raw_data

        self.multiplifier = 1000
        self.country_code = country_code
        self.grid_resolution = grid_resolution

        self.boundary_values = self.__generate_boundary_coordinates(boundary_values)
        self.possible_lon, self.possible_lat = self.__generate_possible_coordinates()
        self.regular_data = self.__generate_regular_data()

    def __get_lon_lat_format(self):
        lon_format, lat_format = set(), set()
        for lon, lat, _ in self.raw_data:
            lon_format.add(abs(Decimal(str(lon)) % 1))
            lat_format.add(abs(Decimal(str(lat)) % 1))
        return ([float(x) for x in coord_type] for coord_type in (lon_format, lat_format))
        # return lon_format, lat_format

    @staticmethod
    def find_nearest(array, value):
        n = [abs(i - value) for i in array]
        idx = n.index(min(n))
        return array[idx]

    def __generate_boundary_coordinates(self, boundary_values: dict) -> dict:
        # TODO add codnitions
        # value_check = value * 100
        # if value_check % 5 == 0 and value_check % 10 != 0:
        if boundary_values:
            for key, value in boundary_values.items():
                formatted_value = int(value * 1000) if "min" in key else int(value * 1000)
                boundary_values[key] = formatted_value
        elif self.country_code:
            boundary_values = {}
            lon_format, lat_format = self.__get_lon_lat_format()
            with open(BOUNDING_BOXES_JSON) as file:
                data = json.load(file)
                for key, bound_coord in zip(("lon_min", "lat_min", "lon_max", "lat_max"), data[self.country_code][1]):
                    sign = -1 if "min" in key else 1
                    format_iterable = lon_format if "lon" in key else lat_format
                    coord_int = int(bound_coord) + sign
                    possible_coords = [coord_int + pos if coord_int > 0 else coord_int - pos for pos in format_iterable]
                    final_value = self.find_nearest(possible_coords, bound_coord)
                    boundary_values[key] = int(final_value * 1000)
        else:
            raise ValueError("Boundary coordinates or country code must be provided")
        # else:
        #     raise ValueError("Coordinate format must be: XX.X5. Actual value: {}".format(value))
        return boundary_values

    def __generate_possible_coordinates(self):
        possible_coords = [[x / self.multiplifier for x in range(self.boundary_values[coord + "_min"],
                                                                 self.boundary_values[coord + "_max"] + 1,
                                                                 int(self.grid_resolution * 1000))]
                           for coord in ("lon", "lat")]
        return possible_coords

    def __generate_regular_data(self):
        regular_data = []
        for row in self.raw_data:
            lon, lat = row[:2]
            if lon in self.possible_lon and lat in self.possible_lat:
                regular_data.append(row)
        regular_data = self.__fill_data_to_array_shape(regular_data)
        return regular_data

    def __fill_data_to_array_shape(self, regular_data: list):
        coordinates = [(row[:2]) for row in self.raw_data]
        for lon in self.possible_lon:
            for lat in self.possible_lat:
                if (lon, lat) not in coordinates:
                    regular_data.append((lon, lat, 0))
        return regular_data

    def sort_data(self) -> None:
        """
        Sort coordinates: south-east -> north-west
        :return:
        """
        self.regular_data.sort(key=lambda x: (-x[0], x[1]))

    @staticmethod
    def __get_exponent(number):
        (sign, digits, exponent) = Decimal(number).as_tuple()
        return len(digits) + exponent - 1

    def zoom_values(self, zoom_value: int, order: int=3):
        values_list = [row[2] for row in self.regular_data]
        values_array = np.array(values_list).reshape(len(self.possible_lon), len(self.possible_lat))
        zoomed = ndimage.zoom(values_array, zoom_value, order=order)
        flatten = zoomed.flatten()
        return flatten

    def zoom_coordinates(self, zoom_value: int):
        coords_coeff = int(self.grid_resolution / zoom_value / 2 * 1000) * (zoom_value - 1)
        exponent = self.__get_exponent(self.grid_resolution)
        final_lon_iterable, final_lat_iterable = \
            ([x / self.multiplifier for x in range(self.boundary_values[coord + "_min"] - coords_coeff,
                                                   self.boundary_values[coord + "_max"] + coords_coeff + 1,
                                                   int(self.multiplifier * 10 ** exponent / zoom_value)
                                                   if exponent != 0 else int(self.multiplifier / zoom_value))]
             for coord in ["lon", "lat"])
        final_coords = []
        for lon in reversed(final_lon_iterable):  # used reversed to have data order SE -> NW
            for lat in final_lat_iterable:
                if (lon, lat) not in final_coords:
                    final_coords.append((lon, lat))
        return final_coords

    def interpolate(self, zoom_value: int, order: int) -> tuple:
        possible_zoom_values = 1, 2, 3, 5, 10, 25
        assert zoom_value in possible_zoom_values, \
            "Chosen zoom value: {} is not in possible zoom values: {}".format(zoom_value, possible_zoom_values)
        self.sort_data()
        zoomed_coordinates = self.zoom_coordinates(zoom_value)
        zoomed_values = self.zoom_values(zoom_value, order)
        return zoomed_coordinates, zoomed_values
