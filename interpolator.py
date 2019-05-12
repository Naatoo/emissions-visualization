import csv
import numpy as np
import scipy.ndimage as ndimage

from geojson import Polygon, Feature, FeatureCollection
from typing import List


class Interpolator:

    def __init__(self, target_file_name: str, raw_data: List[tuple], coordinates: List[tuple], boundary_values) -> None:
        self.target_file_name = target_file_name
        self.raw_data = raw_data
        self.coordinates = coordinates
        self.boundary_values = boundary_values
        self.possible_lat, self.possible_lon = self.__generate_possible_coordinates(boundary_values)
        self.sliced_data = []
        self.slice_data_by_coordinates()

    @staticmethod
    def __generate_possible_coordinates(boundary_values):
        initial_resolution = 0.1
        possible_lat = [x / 1000 for x in range(boundary_values["lat_min"],
                                                boundary_values["lat_max"],
                                                int(initial_resolution * 1000))]
        possible_lon = [x / 1000 for x in range(boundary_values["lon_min"],
                                                boundary_values["lon_max"],
                                                int(initial_resolution * 1000))]
        return possible_lat, possible_lon

    def slice_data_by_coordinates(self):
        for row in self.raw_data:
            lat, lon = row[:2]
            if lat in self.possible_lat and lon in self.possible_lon:
                self.sliced_data.append(row)
        self.__fill_data_to_array_shape()

    def __fill_data_to_array_shape(self):
        for lat in self.possible_lat:
            for lon in self.possible_lon:
                if [lat, lon] not in self.coordinates:
                    self.sliced_data.append((lat, lon, 0))

    def sort_data(self) -> None:
        """
        Sort coordinates: south-east -> north-west
        :return:
        """
        self.sliced_data.sort(key=lambda x: (-x[0], x[1]))

    def zoom_values(self, zoom_value: int):
        values_list = [row[2] for row in self.sliced_data]
        values_array = np.array(values_list).reshape(len(self.possible_lat), len(self.possible_lon))
        zoomed = ndimage.zoom(values_array, zoom_value, order=1)
        flatten = zoomed.flatten()
        return flatten

    def zoom_coordinates(self, zoom_value: int):
        coords_coeff = int(0.1 / zoom_value / 2 * 1000) * (zoom_value - 1)
        final_lat_iterable = [x for x in range(self.boundary_values["lat_min"] - coords_coeff,
                                               self.boundary_values["lat_max"] + coords_coeff,
                                               int(100 / zoom_value))]

        final_lon_iterable = [x for x in range(self.boundary_values["lon_min"] - coords_coeff,
                                               self.boundary_values["lon_max"] + coords_coeff,
                                               int(100 / zoom_value))]
        final_coords = []
        for num_lat in reversed(final_lat_iterable):
            lat = num_lat / 1000
            for num_lon in final_lon_iterable:
                lon = num_lon / 1000
                if (lat, lon) not in final_coords:
                    final_coords.append((lat, lon))
        return final_coords

    def interpolate(self, zoom_value: int):
        self.sort_data()
        zoomed_values = self.zoom_values(zoom_value)
        zoomed_coordinates = self.zoom_coordinates(zoom_value)
        features = []
        values = []
        coeff = 0.1 / zoom_value
        for index, (lat, lon) in enumerate(zoomed_coordinates):
            coords = self.generate_square_coordinates(str(lat), str(lon), coeff=coeff)
            value = zoomed_values[index]
            feature = Feature(
                geometry=Polygon(coords),
                properties={
                    "id": index
                })
            features.append(feature)
            values.append((index, value))
        collection = FeatureCollection(features)
        self.create_files(collection, values)

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

    def create_files(self, collection, values):
        with open("{}.json".format(self.target_file_name), "w") as pm10_json:
            text = {
                "type": "FeatureCollection",
                "features": "{}"
            }
            pm10_json.write(text["features"].format(collection))

        with open('{}.csv'.format(self.target_file_name), 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['id', 'value'])
            for row in values:
                filewriter.writerow(row)
