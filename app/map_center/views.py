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


@map_center.route('/map_by_country', methods=['GET', 'POST'])
def map_by_country():
    form = CountryForm()
    option = "country"
    if form.is_submitted():
        generate_map(form, option)
        return redirect(url_for("map_center.map_by_country"))
    selected_data_str = get_selected_data_str()
    map_exists = True if "m" in globals() else False
    return render_template("map_by_country.html", form=form, selected_data_str=selected_data_str, map_exists=map_exists)


@map_center.route('/map_by_coordinates', methods=['GET', 'POST'])
def map_by_coordinates():
    form = LatLonForm()
    option = "coordinates"
    if form.is_submitted():
        generate_map(form, option)
        return redirect(url_for("map_center.map_by_coordinates"))
    selected_data_str = get_selected_data_str()
    steps = generate_dataset_steps(app.config.get('CURRENT_DATA_HASH', get_hash_of_first_dataset()))
    map_exists = True if "m" in globals() else False
    return render_template("map_by_coordinates.html", form=form, selected_data_str=selected_data_str,
                           steps=steps, map_exists=map_exists)


@map_center.route('/map_render')
def map_render():
    return m.get_root().render()


def generate_map(form, option):
    global m
    zoom_values = int(form.zoom.data)
    order = int(form.interpolation_type.data)
    fill_color = form.color.data
    fill_opacity = form.fill_opacity.data
    line_opacity = form.line_opacity.data

    if option == "country":
        boundaries = None
        default_location = get_country_centroid(form.country.data)
        country_code = form.country.data
    else:
        boundaries = {
            "lon_min": form.lon_min.data,
            "lon_max": form.lon_max.data,
            "lat_min": form.lat_min.data,
            "lat_max": form.lat_max.data
        }
        default_location = generate_coordinates_center(**boundaries)
        country_code = None

    create_files_for_choropleths(boundaries=boundaries,
                                 order=order,
                                 zoom_value=zoom_values,
                                 country_code=country_code)

    m = MapCreator(fill_color=fill_color,
                   fill_opacity=fill_opacity,
                   line_opacity=line_opacity,
                   default_location=default_location).map


def create_files_for_choropleths(zoom_value: int, order: int, boundaries: dict = None, country_code: str = None) -> None:
    dataset_hash, row_data, grid_resolution, bounding_box = prepare_data_for_interpolation(country_code)

    interpolator = Interpolator(row_data, grid_resolution, bounding_box=bounding_box,
                                chosen_boundary_coordinates=boundaries)
    interpolated_coordinates, interpolated_values = interpolator.interpolate(zoom_value, order)

    map_files_creator = DataFilesCreator(interpolated_coordinates, interpolated_values, grid_resolution, zoom_value,
                                         country_code)
    map_files_creator.create_files()


def prepare_data_for_interpolation(country_code: str=None):
    dataset_hash = app.config.get('CURRENT_DATA_HASH', get_hash_of_first_dataset())
    row_data = get_dataset(dataset_hash)
    grid_resolution = get_data_metadata(dataset_hash).grid_resolution
    bounding_box = get_country_bounding_box(country_code) if country_code else None
    return dataset_hash, row_data, grid_resolution, bounding_box
