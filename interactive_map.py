import folium
import os
import pandas as pd
from selenium import webdriver


class InteractiveMap:

    def __init__(self, file_name: str, layer_name: str, fill_color: str,
                 fill_opacity: float, line_opacity: float=0) -> None:
        self.file_name = file_name
        self.csv_file = self._read_csv()

        self.columns_names = ['id', 'value']
        self.key_on_column = 'id'
        self.layer_name = layer_name
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.line_opacity = line_opacity

        self.default_location = [50, 20]
        self.default_zoom = 7
        self.map = self._create_map()

        self.target_name = None
        self.target_directory = os.getcwd()

    def _read_csv(self):
        return pd.read_csv("{}.csv".format(self.file_name))

    def _create_choropleth(self) -> folium.Choropleth:
        choropleth = folium.Choropleth(
            geo_data="{}.json".format(self.file_name),
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
        map_folium = folium.Map(location=self.default_location, zoom_start=self.default_zoom)
        map_folium.add_child(self._create_choropleth())
        map_folium.add_child(folium.LayerControl())
        return map_folium

    def write_to_file(self, target_name: str=None, target_directory: str=None) -> None:
        self.target_name = target_name if target_name else self.file_name
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
