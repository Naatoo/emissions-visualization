import folium
import os
import pandas as pd

from app.tools.paths import COORDINATES_FILE, VALUES_FILE


class MapCreator:

    def __init__(self, fill_color: str, fill_opacity: float, line_opacity: float=0,
                 default_location: tuple=(50, 20), default_zoom: int=6) -> None:
        self.file_name = "PM10_zoomed"
        self.csv_file = self._read_csv()

        self.columns_names = ['id', 'value']
        self.key_on_column = 'id'
        self.layer_name = "Layer"
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.line_opacity = line_opacity

        self.default_location = default_location
        self.default_zoom = default_zoom
        self.map = self._create_map()

        self.target_name = None
        self.target_directory = os.getcwd()

    def _read_csv(self):
        return pd.read_csv(VALUES_FILE)

    def _create_choropleth(self) -> folium.Choropleth:
        choropleth = folium.Choropleth(
            geo_data=COORDINATES_FILE,
            name=self.layer_name,
            data=self.csv_file,
            columns=self.columns_names,
            key_on='feature.properties.{}'.format(self.key_on_column),
            fill_color=self.fill_color,
            fill_opacity=self.fill_opacity,
            line_opacity=self.line_opacity
        )
        return choropleth

    def _create_map(self) -> folium.Map:
        map_folium = folium.Map(location=self.default_location, zoom_start=self.default_zoom, control_scale=True,
                                prefer_canvas=True)
        map_folium.add_child(self._create_choropleth())
        folium.LatLngPopup().add_to(map_folium)
        folium.ClickForMarker().add_to(map_folium)
        folium.TileLayer('openstreetmap').add_to(map_folium)
        folium.TileLayer('Mapbox Bright').add_to(map_folium)
        folium.TileLayer('Stamen Terrain').add_to(map_folium)
        folium.TileLayer('Stamen Toner').add_to(map_folium)
        folium.TileLayer('Stamen Watercolor').add_to(map_folium)
        folium.TileLayer('CartoDB positron').add_to(map_folium)
        folium.TileLayer('CartoDB dark_matter').add_to(map_folium)
        folium.TileLayer('Mapbox Control Room').add_to(map_folium)
        map_folium.add_child(folium.LayerControl())
        return map_folium
