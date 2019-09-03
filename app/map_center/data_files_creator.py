import csv
from typing import Generator

import reverse_geocode
from geojson import Feature, Polygon, FeatureCollection

from app.tools.exceptions import NoChosenCoordsInDatasetException
from app.tools.paths import COORDINATES_FILE, VALUES_FILE


class DataFilesCreator:
    def __init__(self, coordinates: list, values: list, lon_resolution: float, lat_resolution: float, zoom_value: int,
                 country_code: str=None) -> None:
        self.lon_resolution = lon_resolution
        self.lat_resolution = lat_resolution
        self.zoom_value = zoom_value
        self.country_code = country_code

        self.collection, self.indexed_values = self._generate_collection_indexed_values(coordinates, values)

    def _interpolated_data_generator(self, coordinates, values):
        lon_coeff = self.lon_resolution / self.zoom_value
        lat_coeff = self.lat_resolution / self.zoom_value
        for index, (lon, lat) in enumerate(coordinates):
            if reverse_geocode.get((lat, lon))["country_code"] == self.country_code or self.country_code is None:
                coords = self.generate_square_coordinates(str(lon), str(lat), lon_coeff, lat_coeff)
                value = values[index]
                if value > 1:
                    yield coords, value

    def _generate_collection_indexed_values(self, coordinates, values):
        features = []
        final_values = []
        for index, (coords, value) in enumerate(self._interpolated_data_generator(coordinates, values)):
                feature = Feature(geometry=Polygon(coords), properties={"id": index})
                features.append(feature)
                final_values.append((index, value))
        collection = FeatureCollection(features)
        if not final_values and self.country_code:
            raise NoChosenCoordsInDatasetException
        return collection, final_values

    @staticmethod
    def generate_square_coordinates(lon: str, lat: str, lon_coeff: float, lat_coeff: float) -> list:
        lon_scale = lon_coeff * 0.5
        lat_scale = lat_coeff * 0.5
        components = (-1, -1), (1, -1), (1, 1), (-1, 1)
        l = []
        for x_ch, y_ch in components:
            a = float(lon) + x_ch * lon_scale
            b = float(lat) + y_ch * lat_scale
            l.append((a, b))
        return [l]

    def create_files(self) -> bool:
        if self.indexed_values:
            with open(COORDINATES_FILE, "w") as coordinates_file:
                text = {
                    "type": "FeatureCollection",
                    "features": "{}"
                }
                coordinates_file.write(text["features"].format(self.collection))

            with open(VALUES_FILE, 'w') as values_file:
                filewriter = csv.writer(values_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                filewriter.writerow(['id', 'value'])
                for row in self.indexed_values:
                    filewriter.writerow(row)
            files_created = True
        else:
            files_created = False
        return files_created
