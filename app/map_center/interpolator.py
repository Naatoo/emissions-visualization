import csv
import numpy as np
import scipy.ndimage as ndimage

from geojson import Polygon, Feature, FeatureCollection
from typing import List, Tuple

from app.tools.paths import PM10_CSV_FILE, PM10_JSON_FILE, BOUNDING_BOXES_JSON
import itertools
import reverse_geocode
import json
from decimal import Decimal


class Interpolator:

    def __init__(self, raw_data: List[tuple], coordinates: List[tuple], boundary_values=None, country_code=None) -> None:
        self.raw_data = raw_data
        self.coordinates = coordinates
        self.multiplifier = 1000
        self.country_code = country_code
        self.grid_resolution_degree = self.__generate_grid_resolution_degree()

        self.boundary_values = self.__generate_boundary_coordinates(boundary_values)

        self.possible_lon, self.possible_lat = self.__generate_possible_coordinates()

        self.sliced_data = []
        self.slice_data_by_coordinates()

    def __generate_grid_resolution_degree(self):
        lon_1, lat_1, lon_2, lat_2 = list(itertools.chain(*(self.raw_data[index][:2] for index in range(2))))
        res = abs(lon_1) - abs(lon_2) if lon_1 != lon_2 else abs(lat_1) - abs(lat_2)
        if res != 0:
            abs_res = abs(res)
        else:
            raise ValueError(f"Wrong coordinates. Longitude {lon_1}, {lon_2}"
                             f"and latitude {lat_1}, {lat_2} of first two points are identical.")
        return abs_res

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
                           int(self.grid_resolution_degree * 1000))]
                           for coord in ("lon", "lat")]
        return possible_coords

    def slice_data_by_coordinates(self):
        for row in self.raw_data:
            lon, lat = row[:2]
            if lon in self.possible_lon and lat in self.possible_lat:
                if row in self.sliced_data:
                    print(row)
                self.sliced_data.append(row)
        self.__fill_data_to_array_shape()

    def __fill_data_to_array_shape(self):
        for lon in self.possible_lon:
            for lat in self.possible_lat:
                if (lon, lat) not in self.coordinates:
                    self.sliced_data.append((lon, lat, 0))

    def sort_data(self) -> None:
        """
        Sort coordinates: south-east -> north-west
        :return:
        """
        self.sliced_data.sort(key=lambda x: (-x[0], x[1]))

    @staticmethod
    def __get_exponent(number):
        (sign, digits, exponent) = Decimal(number).as_tuple()
        return len(digits) + exponent - 1

    def zoom_values(self, zoom_value: int, order: int=3):
        values_list = [row[2] for row in self.sliced_data]
        values_array = np.array(values_list).reshape(len(self.possible_lon), len(self.possible_lat))
        zoomed = ndimage.zoom(values_array, zoom_value, order=order)
        flatten = zoomed.flatten()
        return flatten

    def zoom_coordinates(self, zoom_value: int):
        coords_coeff = int(self.grid_resolution_degree / zoom_value / 2 * 1000) * (zoom_value - 1)
        exponent = self.__get_exponent(self.grid_resolution_degree)
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

    def interpolate(self, zoom_value: int, order: int) -> None:
        possible_zoom_values = 1, 2, 3, 5, 10, 25
        assert zoom_value in possible_zoom_values, \
            "Chosen zoom value: {} is not in possible zoom values: {}".format(zoom_value, possible_zoom_values)
        self.sort_data()
        zoomed_values = self.zoom_values(zoom_value, order)
        zoomed_coordinates = self.zoom_coordinates(zoom_value)
        features = []
        values = []
        coeff = self.grid_resolution_degree / zoom_value
        data_for_heatmap = []
        for index, (lon, lat) in enumerate(zoomed_coordinates):
            if reverse_geocode.get((lat, lon))["country_code"] == self.country_code or self.country_code is None:
                data_for_heatmap.append((lon, lat, zoomed_values[index]))
                coords = self.generate_square_coordinates(str(lon), str(lat), coeff=coeff)
                value = zoomed_values[index]
                feature = Feature(
                    geometry=Polygon(coords),
                    properties={
                        "id": index
                    })
                features.append(feature)
                values.append((index, value))
        collection = FeatureCollection(features)
        self.create_files(collection, values, data_for_heatmap)
        # TODO do not draw choropleth if value=0

    @staticmethod
    def generate_square_coordinates(lat: str, lon: str, coeff) -> list:
        grid_scale = coeff * 0.5
        components = (-1, -1), (1, -1), (1, 1), (-1, 1)
        l = []
        for x_ch, y_ch in components:
            a = float(lat) + x_ch * grid_scale
            b = float(lon) + y_ch * grid_scale
            l.append((a, b))
        return [l]

    @staticmethod
    def create_files(collection, values, data_for_heatmap):
        # with open("{}.json".format(self.target_file_name), "w") as pm10_json:
        with open(PM10_JSON_FILE, "w") as pm10_json:
            text = {
                "type": "FeatureCollection",
                "features": "{}"
            }
            pm10_json.write(text["features"].format(collection))

        # with open('{}.csv'.format(self.target_file_name), 'w') as csvfile:
        with open(PM10_CSV_FILE, 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['id', 'value'])
            for row in values:
                filewriter.writerow(row)
        #
        # with open("{}_heatmap_data.txt".format(self.target_file_name), "w") as heatmap_txt:
        #     for row in data_for_heatmap:
        #         heatmap_txt.writelines("{},{},{}\n".format(*row))
