from flask import current_app as app
from flask import render_template, redirect, url_for

from app.database.queries import get_selected_data_str, get_dataset, get_hash_of_first_dataset, get_data_metadata, \
    get_country_bounding_box, get_country_centroid
from app.map_center import map_center
from app.map_center.data_files_creator import DataFilesCreator
from app.map_center.forms import LatLonForm, CountryForm
from app.map_center.map_creator import MapCreator
from app.map_center.interpolator import Interpolator
from app.map_center.utils import generate_dataset_steps, generate_coordinates_center


def prepare_data_for_map(zoom_value: int, boundaries: dict = None, country_code: str = None, order: int=3) -> None:
    dataset_hash = app.config.get('CURRENT_DATA_HASH', get_hash_of_first_dataset())
    # TODO handle not dataset_hash on the startup
    row_data = get_dataset(dataset_hash)
    grid_resolution = get_data_metadata(dataset_hash).grid_resolution
    bounding_box = get_country_bounding_box(country_code) if country_code else None

    interpolator = Interpolator(row_data, grid_resolution, bounding_box=bounding_box, chosen_boundary_coordinates=boundaries)
    interpolated_coordinates, interpolated_values = interpolator.interpolate(zoom_value, order)

    map_files_creator = DataFilesCreator(interpolated_coordinates, interpolated_values, grid_resolution, zoom_value,
                                         country_code)
    map_files_creator.create_files()


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

        m = MapCreator(fill_color="Oranges",
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
                             zoom_value=int(form.zoom.data),
                             order=int(form.interpolation_type.data))

        m = MapCreator(fill_color=form.color.data,
                       fill_opacity=form.fill_opacity.data,
                       line_opacity=form.line_opacity.data,
                       default_location=generate_coordinates_center(**boundaries)).map


def generate_map_by_country(form=None):
    global m
    if not form:
        prepare_data_for_map(zoom_value=2, country_code="LU")

        m = MapCreator(fill_color="Oranges",
                       fill_opacity=0.8,
                       line_opacity=0.3,
                       default_location=(50, 20),
                       default_zoom=8).map
    else:
        prepare_data_for_map(country_code=form.country.data,
                             zoom_value=int(form.zoom.data),
                             order=int(form.interpolation_type.data))

        m = MapCreator(fill_color=form.color.data,
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
    steps = generate_dataset_steps(app.config.get('CURRENT_DATA_HASH', get_hash_of_first_dataset()))
    return render_template("map_by_coordinates.html", form=form, selected_data_str=selected_data_str, steps=steps)


@map_center.route('/map_by_country', methods=['GET', 'POST'])
def map_by_country():
    form = CountryForm()
    if form.is_submitted():
        generate_map_by_country(form)
        return redirect(url_for("map_center.map_by_country"))
    selected_data_str = get_selected_data_str()
    return render_template("map_by_country.html", form=form, selected_data_str=selected_data_str)
