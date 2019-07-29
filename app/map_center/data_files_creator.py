import csv

import reverse_geocode
from geojson import Feature, Polygon, FeatureCollection

from app.tools.paths import COORDINATES_FILE, VALUES_FILE


class DataFilesCreator:
    def __init__(self, coordinates: list, values: list, grid_resolution: float, zoom_value: int,
                 country_code: str=None) -> None:
        self.grid_resolution = grid_resolution
        self.zoom_value = zoom_value
        self.country_code = country_code
        self.collection, self.indexed_values = self._generate_collection_indexed_values(coordinates, values)

    def _generate_collection_indexed_values(self, zoomed_coordinates, zoomed_values):
        features = []
        final_values = []
        coeff = self.grid_resolution / self.zoom_value
        for index, (lon, lat) in enumerate(zoomed_coordinates):
            if reverse_geocode.get((lat, lon))["country_code"] == self.country_code or self.country_code is None:
                coords = self.generate_square_coordinates(str(lon), str(lat), coeff=coeff)
                value = zoomed_values[index]
                if value > 0.01:
                    feature = Feature(geometry=Polygon(coords), properties={"id": index})
                    features.append(feature)
                    final_values.append((index, value))
        collection = FeatureCollection(features)
        return collection, final_values

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

    def create_files(self):
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
