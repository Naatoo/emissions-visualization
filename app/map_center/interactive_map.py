import folium
import os
import pandas as pd
from selenium import webdriver

from app.tools.paths import PM10_CSV_FILE, PM10_JSON_FILE


class InteractiveMap:

    def __init__(self, fill_color: str, fill_opacity: float, line_opacity: float=0,
                 default_location: tuple=(50, 20), default_zoom: int=9) -> None:
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
        return pd.read_csv(PM10_CSV_FILE)

    def _create_choropleth(self) -> folium.Choropleth:
        choropleth = folium.Choropleth(
            geo_data=PM10_JSON_FILE,
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
        map_folium = folium.Map(location=self.default_location, zoom_start=self.default_zoom, control_scale=True)
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

    def write_to_file(self, target_name: str=None, target_directory: str=None) -> None:
        self.target_name = target_name if target_name else "{}.html".format(self.file_name)
        self.target_directory = target_directory if target_directory else self.target_directory
        self.map.save(self.target_name)

    def run_map_and_freeze(self) -> None:
        url = 'file://{path}/{mapfile}'.format(path=self.target_directory, mapfile=self.target_name)
        try:
            browser = webdriver.Firefox(executable_path="geckodriver", )
            browser.maximize_window()
            browser.get(url)
            breakpoint()
        finally:
            browser.quit()
