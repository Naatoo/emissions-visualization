import numpy as np
import scipy.ndimage as ndimage

from decimal import Decimal
from typing import List, Optional, Generator

from app.tools.exceptions import NoChosenCoordsInDatasetException


class Interpolator:

    def __init__(self, raw_data: List[tuple], grid_resolution: float, bounding_box: tuple = None,
                 chosen_boundary_coordinates: dict = None) -> None:
        self.raw_data = raw_data
        self.multiplifier = 1000
        self.grid_resolution = grid_resolution

        self.boundaries = self.__generate_boundaries(bounding_box, chosen_boundary_coordinates)
        self.multiplified_boundaries = self.multiplify_boundaries()
        self.possible_lon, self.possible_lat = self.__generate_chosen_coordinates()
        self.regular_data = self.__generate_regular_data()

    def __generate_boundaries(self, bounding_box: Optional[tuple], chosen_boundary_coordinates: Optional[dict]) -> dict:
        if bounding_box and chosen_boundary_coordinates:
            raise ValueError(
                "Only one type on generation can be chosen: by country bounding box or by chosen coordinates")
        elif bounding_box:
            boundaries = self.__generate_boundaries_by_country(bounding_box)
        elif chosen_boundary_coordinates:
            boundaries = self.__generate_boundaries_by_coordinates(chosen_boundary_coordinates)
        else:
            raise ValueError("Both parameters (bounding_box and chosen_boundary_coordinates) cannot be None")
        return boundaries

    def __generate_boundaries_by_country(self, bounding_box: Optional[tuple]) -> dict:
        boundary_coordinates = {}
        lon_format, lat_format = self.__get_lon_lat_format()
        for key, bound_coord in zip(("lon_min", "lon_max", "lat_min", "lat_max"), bounding_box):
            sign = -1 if "min" in key else 1
            format_iterable = lon_format if "lon" in key else lat_format
            coord_int = int(bound_coord) + sign
            possible_coords = [coord_int + pos if coord_int > 0 else coord_int - pos for pos in format_iterable]
            final_value = self.find_nearest(possible_coords, bound_coord)
            boundary_coordinates[key] = final_value
        return boundary_coordinates

    def __generate_boundaries_by_coordinates(self, chosen_coords: dict) -> dict:
        boundary_coordinates = {}
        for coord in "min", "max":
            dataset_lon = [item[0] for item in self.raw_data]
            boundary_coordinates[f"lon_{coord}"] = self.find_nearest(dataset_lon, float(chosen_coords[f"lon_{coord}"]))
            dataset_lat = [item[1] for item in self.raw_data if item[0] == boundary_coordinates["lon_min"]]
            boundary_coordinates[f"lat_{coord}"] = self.find_nearest(dataset_lat, float(chosen_coords[f"lat_{coord}"]))

        cond = any((any((boundary_coordinates["lon_max"] < chosen_coords["lon_min"],
                         boundary_coordinates["lon_min"] > chosen_coords["lon_max"])),
                    any((boundary_coordinates["lon_max"] < chosen_coords["lon_min"],
                         boundary_coordinates["lat_min"] > chosen_coords["lat_max"]))))
        if cond:
            raise NoChosenCoordsInDatasetException
        return boundary_coordinates

    def __get_lon_lat_format(self) -> Generator[list, None, None]:
        lon_format, lat_format = set(), set()
        for lon, lat, _ in self.raw_data:
            lon_format.add(abs(Decimal(str(lon)) % 1))
            lat_format.add(abs(Decimal(str(lat)) % 1))
        return ([float(x) for x in coord_type] for coord_type in (lon_format, lat_format))

    @staticmethod
    def find_nearest(iterable: list, value: float) -> float:
        diffs = [abs(i - value) for i in iterable]
        nearest_id = diffs.index(min(diffs))
        return iterable[nearest_id]

    def multiplify_boundaries(self):
        return {key: int(value * self.multiplifier) for key, value in self.boundaries.items()}

    def __generate_chosen_coordinates(self):
        possible_coords = [
            [x / self.multiplifier for x in range(self.multiplified_boundaries[coord + "_min"],
                                                  self.multiplified_boundaries[coord + "_max"] + 1,
                                                  int(self.grid_resolution * self.multiplifier))]
            for coord in ("lon", "lat")]
        return possible_coords

    def __generate_regular_data(self):
        regular_data = []
        for row in self.raw_data:
            lon, lat = row[:2]
            if lon in self.possible_lon and lat in self.possible_lat:
                regular_data.append(row)
        regular_data = self.__fill_data_to_array_shape(regular_data)
        regular_data.sort(key=lambda x: (-x[0], x[1]))
        return regular_data

    def __fill_data_to_array_shape(self, regular_data: list):
        coordinates = [(row[:2]) for row in self.raw_data]
        for lon in self.possible_lon:
            for lat in self.possible_lat:
                if (lon, lat) not in coordinates:
                    regular_data.append((lon, lat, 0))
        return regular_data

    def interpolate(self, zoom_value: int, order: int) -> tuple:
        zoomed_coordinates = self.zoom_coordinates(zoom_value)
        zoomed_values = self.zoom_values(zoom_value, order)
        return zoomed_coordinates, zoomed_values

    def zoom_values(self, zoom_value: int, order: int = 3):
        values_list = [row[2] for row in self.regular_data]
        values_array = np.array(values_list).reshape(len(self.possible_lon), len(self.possible_lat))
        zoomed = ndimage.zoom(values_array, zoom_value, order=order)
        flatten = zoomed.flatten()
        return flatten

    def zoom_coordinates(self, zoom_value: int):
        coords_coeff = int(self.grid_resolution / zoom_value / 2 * self.multiplifier) * (zoom_value - 1)
        exponent = self.__get_exponent(self.grid_resolution)
        grid_step = int(self.multiplifier * 10 ** exponent / zoom_value) \
            if exponent != 0 else int(self.multiplifier / zoom_value)
        final_lon_iterable, final_lat_iterable = \
            ([x / self.multiplifier for x in range(self.multiplified_boundaries[coord + "_min"] - coords_coeff,
                                                   self.multiplified_boundaries[coord + "_max"] + coords_coeff + 1,
                                                   grid_step)]
             for coord in ["lon", "lat"])
        final_coords = []
        for lon in reversed(final_lon_iterable):  # used reversed to have data order SE -> NW
            for lat in final_lat_iterable:
                if (lon, lat) not in final_coords:
                    final_coords.append((lon, lat))
        return final_coords

    @staticmethod
    def __get_exponent(number):
        (sign, digits, exponent) = Decimal(number).as_tuple()
        return len(digits) + exponent - 1
