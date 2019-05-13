import csv
import numpy as np
import scipy.ndimage as ndimage

from geojson import Polygon, Feature, FeatureCollection
from typing import List, Tuple


class Interpolator:

    def __init__(self, target_file_name: str, raw_data: List[tuple], coordinates: List[tuple], boundary_values) -> None:
        self.target_file_name = target_file_name
        self.raw_data = raw_data
        self.coordinates = coordinates
        self.boundary_values = self.__generate_boundary_coordinates(boundary_values)
        self.grid_resolution_degree = 0.1
        self.possible_lat, self.possible_lon = self.__generate_possible_coordinates()

        self.sliced_data = []
        self.slice_data_by_coordinates()

    @staticmethod
    def __generate_boundary_coordinates(boundary_values: dict) -> dict:
        for key, value in boundary_values.items():
            value_check = value * 100
            if value_check % 5 == 0 and value_check % 10 != 0:
                formatted_value = int(value * 1000) if "min" in key else int(value * 1000 + 1)
                boundary_values[key] = formatted_value
            else:
                raise ValueError("Coordinate format must be: XX.X5. Actual value: {}".format(value))
        return boundary_values

    def __generate_possible_coordinates(self) -> Tuple[list, list]:
        possible_lat = [x / 1000 for x in range(self.boundary_values["lat_min"],
                                                self.boundary_values["lat_max"],
                                                int(self.grid_resolution_degree * 1000))]
        possible_lon = [x / 1000 for x in range(self.boundary_values["lon_min"],
                                                self.boundary_values["lon_max"],
                                                int(self.grid_resolution_degree * 1000))]
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

    def zoom_values(self, zoom_value: int, order: int=3):
        values_list = [row[2] for row in self.sliced_data]
        values_array = np.array(values_list).reshape(len(self.possible_lat), len(self.possible_lon))
        zoomed = ndimage.zoom(values_array, zoom_value, order=order)
        flatten = zoomed.flatten()
        return flatten

    def zoom_coordinates(self, zoom_value: int):
        coords_coeff = int(self.grid_resolution_degree / zoom_value / 2 * 1000) * (zoom_value - 1)
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
        for index, (lat, lon) in enumerate(zoomed_coordinates):
            data_for_heatmap.append((lat, lon, zoomed_values[index]))
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
        self.create_files(collection, values, data_for_heatmap)

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

    def create_files(self, collection, values, data_for_heatmap):
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

        with open("{}_heatmap_data.txt".format(self.target_file_name), "w") as heatmap_txt:
            for row in data_for_heatmap:
                heatmap_txt.writelines("{},{},{}\n".format(*row))
