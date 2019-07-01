from flask import current_app as app
from flask import render_template, redirect, url_for
from numpy import mean

import pandas

from app.database.queries import get_selected_data_str
from app.map_center import map_center
from app.map_center.forms import LatLonForm, CountryForm
from app.map_center.interactive_map import InteractiveMap
from app.map_center.interpolator import Interpolator
from app.models.data_models import DataValues, DataInfo
from app.tools.paths import COUNTRIES_CENTROIDS_CSV


def prepare_data_for_map(zoom_value: int, boundaries: dict=None, country_code: str= None) -> None:
    order = 5
    row_data = get_data_from_database()
    interpolator = Interpolator(row_data, [(row[:2]) for row in row_data], boundary_values=boundaries, country_code=country_code)
    interpolator.interpolate(zoom_value=zoom_value, order=order)


def get_data_from_database():
    dataset_hash = app.config.get('CURRENT_DATA_HASH') # TODO handle not dataset_hash on the startup
    if not dataset_hash:
        dataset_hash = DataInfo.query.all()[0].dataset_hash
    row_data = []
    for row in DataValues.query.filter_by(dataset_hash=dataset_hash):
        row_data.append((row.lon, row.lat, row.value))
    return row_data


def generate_map_by_coordinates(form=None):
    global m
    if not form:
        boundaries = {
            "lon_min": 10,
            "lon_max": 20,
            "lat_min": 30.9,
            "lat_max": 40.9
        }
        prepare_data_for_map(boundaries=boundaries,
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
        prepare_data_for_map(boundaries=boundaries,
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
        prepare_data_for_map(zoom_value=2, country_code="LU")

        m = InteractiveMap(fill_color="Oranges",
                           fill_opacity=0.8,
                           line_opacity=0.3,
                           default_location=(50, 20),
                           default_zoom=8).map
    else:
        prepare_data_for_map(country_code=form.country.data,
                             zoom_value=int(form.interpolation.data))

        m = InteractiveMap(fill_color=form.color.data,
                           fill_opacity=form.fill_opacity.data,
                           line_opacity=form.line_opacity.data,
                           default_location=get_country_centroid(form.country.data)
                           ).map


@map_center.route('/map_render')
def map_render():
    return m.get_root().render()


@map_center.route('/map_by_coordinates', methods=['GET', 'POST'])
def map_by_coordinates():
    form = LatLonForm()
    if form.is_submitted():
        generate_map_by_coordinates(form)
        return redirect(url_for("map_center.map_by_coordinates"))
    selected_data_str = get_selected_data_str()
    return render_template("map_by_coordinates.html", form=form, selected_data_str=selected_data_str)


@map_center.route('/map_by_country', methods=['GET', 'POST'])
def map_by_country():
    form = CountryForm()
    if form.is_submitted():
        generate_map_by_country(form)
        return redirect(url_for("map_center.map_by_country"))
    selected_data_str = get_selected_data_str()
    return render_template("map_by_country.html", form=form, selected_data_str=selected_data_str)
