from flask import render_template, redirect, url_for
from numpy import mean
import pandas

from app.map_tools.csv_parser import CSVFileParser
from app.map_tools.excel_parser import ExcelFileParser
from app.map_tools.interpolator import Interpolator
from app.map_tools.interactive_map import InteractiveMap

from app.home import home
from app.home.map_zoom_form import LatLonForm, CountryForm

from app.tools.paths import PM10_RAW_FILE
from app.tools.paths import EMISSION_EXCEL_FILE, COUNTRIES_CENTROIDS_CSV


def create_csv_json_files(zoom_value: int, boundaries: dict=None, country_code: str= None) -> None:
    order = 5
    source_file_name = PM10_RAW_FILE
    # source_file_name = EMISSION_EXCEL_FILE
    target_file_name = "PM10_zoomed"
    # country_code = "PL"
    parser = CSVFileParser(source_file_name, **{"country": country_code})
    # parser = ExcelFileParser(source_file_name, **{"country": country_code})
    interpolator = Interpolator(parser.data, parser.coordinates, boundary_values=boundaries, country_code=country_code)
    interpolator.interpolate(zoom_value=zoom_value, order=order)


def generate_map_by_coordinates(form=None):
    global m
    if not form:
        boundaries = {
            "lon_min": 10,
            "lon_max": 20,
            "lat_min": 30.9,
            "lat_max": 40.9
        }
        create_csv_json_files(boundaries=boundaries,
                              zoom_value=2)

        m = InteractiveMap(fill_color="Oranges",
                           fill_opacity=0.8,
                           line_opacity=0.3,
                           default_location=(50, 20),
                           default_zoom=8).map
    else:
        boundaries = {
            "lon_min": form.lon_min.data,
            "lon_max": form.lon_max.data,
            "lat_min": form.lat_min.data,
            "lat_max": form.lat_max.data
        }
        create_csv_json_files(boundaries=boundaries,
                              zoom_value=int(form.interpolation.data))

        default_lon = mean([boundaries["lat_min"], boundaries["lat_max"]]) / 1000
        default_lat = mean([boundaries["lon_min"], boundaries["lon_max"]]) / 1000
        m = InteractiveMap(fill_color=form.color.data,
                           fill_opacity=form.fill_opacity.data,
                           line_opacity=form.line_opacity.data,
                           default_location=(default_lon, default_lat)).map


def get_country_centroid(expected_country_code: str):
    data = pandas.read_csv(COUNTRIES_CENTROIDS_CSV)
    for lon, lat, country_code in zip(data['lon'], data['lat'], data['code']):
        if expected_country_code == country_code:
            center_coordinates = lat, lon
    return center_coordinates


def generate_map_by_country(form=None):
    global m
    if not form:
        create_csv_json_files(zoom_value=2, country_code="LU")

        m = InteractiveMap(fill_color="Oranges",
                           fill_opacity=0.8,
                           line_opacity=0.3,
                           default_location=(50, 20),
                           default_zoom=8).map
    else:
        create_csv_json_files(country_code=form.country.data,
                              zoom_value=int(form.interpolation.data))

        m = InteractiveMap(fill_color=form.color.data,
                           fill_opacity=form.fill_opacity.data,
                           line_opacity=form.line_opacity.data,
                           default_location=get_country_centroid(form.country.data)
                           ).map


@home.route('/map_render')
def map_render():
    return m.get_root().render()


@home.route('/map_by_coordinates', methods=['GET', 'POST'])
def map_by_coordinates():
    form = LatLonForm()
    if form.is_submitted():
        generate_map_by_coordinates(form)
        return redirect(url_for("home.map_by_coordinates"))
    return render_template("map_by_coordinates.html", form=form)


@home.route('/map_by_country', methods=['GET', 'POST'])
def map_by_country():
    form = CountryForm()
    if form.is_submitted():
        generate_map_by_country(form)
        return redirect(url_for("home.map_by_country"))
    return render_template("map_by_country.html", form=form)
