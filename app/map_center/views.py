from flask import current_app as app, flash, request
from flask import render_template, redirect, url_for
from flask_login import login_required

from app.database.queries import get_selected_data_str, get_dataset, get_data_metadata, \
    get_country_bounding_box, get_country_centroid, assert_lon_lat_resolution_identical, \
    get_boundary_values_for_dataset, get_country_name
from app.map_center import map_center
from app.map_center.data_files_creator import DataFilesCreator
from app.map_center.forms import LatLonForm, CountryForm, MapForm
from app.map_center.map_creator import MapCreator
from app.map_center.interpolator import Interpolator
from app.map_center.utils import generate_coordinates_center
from app.tools.exceptions import LonLatResolutionException, NoChosenCoordsInDatasetException


@map_center.route('/map/country', methods=['GET', 'POST'])
@login_required
def map_by_country():
    name = 'map_by_country'
    form = CountryForm()
    option = "country"
    form_sent = False
    if request.args and request.method == "GET":
        form.color.default = request.args.get("color")
        form.fill_opacity.default = request.args.get("fill_opacity")
        form.line_opacity.default = request.args.get("line_opacity")
        form.interpolation_type.default = request.args.get("interpolation_type")
        form.zoom.default = request.args.get("zoom")
        form.country.default = request.args.get("country")
        form.process()
        form_sent = True
    if form.is_submitted():
        generate_map(form, option, name)
        return redirect(url_for(f"map_center.{name}",
                                color=form.color.data,
                                fill_opacity=form.fill_opacity.data,
                                line_opacity=form.line_opacity.data,
                                zoom=form.zoom.data,
                                interpolation_type=form.interpolation_type.data,
                                country=form.country.data,
                                ))
    selected_data_str = get_selected_data_str()
    map_exists = True if "m" in globals() and form_sent else False
    return render_template(f"{name}.html", form=form, selected_data_str=selected_data_str, map_exists=map_exists)


@map_center.route('/map/coordinates', methods=['GET', 'POST'])
@login_required
def map_by_coordinates():
    name = 'map_by_coordinates'
    form = LatLonForm()
    option = "coordinates"
    form_sent = False
    if request.args and request.method == "GET":
        form.color.default = request.args.get("color")
        form.fill_opacity.default = request.args.get("fill_opacity")
        form.line_opacity.default = request.args.get("line_opacity")
        form.interpolation_type.default = request.args.get("interpolation_type")
        form.zoom.default = request.args.get("zoom")
        form.lon_min.default = float(request.args.get("lon_min"))
        form.lon_max.default = float(request.args.get("lon_max"))
        form.lat_min.default = float(request.args.get("lat_min"))
        form.lat_max.default = float(request.args.get("lat_max"))
        form.process()
        form_sent = True
    if form.is_submitted():
        generate_map(form, option, name)
        return redirect(url_for(f"map_center.{name}",
                                color=form.color.data,
                                fill_opacity=form.fill_opacity.data,
                                line_opacity=form.line_opacity.data,
                                zoom=form.zoom.data,
                                interpolation_type=form.interpolation_type.data,
                                lon_min=form.lon_min.data,
                                lon_max=form.lon_max.data,
                                lat_min=form.lat_min.data,
                                lat_max=form.lat_max.data,
                                ))
    selected_data_str = get_selected_data_str()
    map_exists = True if "m" in globals() and form_sent else False
    return render_template(f"{name}.html", form=form, selected_data_str=selected_data_str, map_exists=map_exists)


@map_center.route('/map/dataset', methods=['GET', 'POST'])
@login_required
def map_whole_dataset():
    name = 'map_whole_dataset'
    form = MapForm()
    option = "whole_dataset"
    form_sent = False
    if request.args and request.method == "GET":
        form.color.default = request.args.get("color")
        form.fill_opacity.default = request.args.get("fill_opacity")
        form.line_opacity.default = request.args.get("line_opacity")
        form.process()
        form_sent = True
    if form.is_submitted():
        generate_map(form, option, name)
        return redirect(url_for(f"map_center.{name}",
                                color=form.color.data,
                                fill_opacity=form.fill_opacity.data,
                                line_opacity=form.line_opacity.data,
                                ))
    selected_data_str = get_selected_data_str()
    map_exists = True if "m" in globals() and form_sent else False
    return render_template("map_base.html", form=form, selected_data_str=selected_data_str, map_exists=map_exists)


@map_center.route('/map_render')
@login_required
def map_render():
    return m.get_root().render()


def generate_map(form, option, name):
    try:
        dataset_hash = app.config['CURRENT_DATA_HASH']
    except KeyError:
        flash(f"No dataset selected.", category="warning")
        return redirect(url_for(f"map_center.{name}"))
    global m
    if "m" in globals():
        del m
    fill_color = form.color.data
    fill_opacity = form.fill_opacity.data
    line_opacity = form.line_opacity.data

    if option in ("country", "coordinates"):
        try:
            assert_lon_lat_resolution_identical(dataset_hash)
        except LonLatResolutionException:
            flash(f"Longitude and latitude resolution is not equal. Interpolation impossible. "
                  f"Please choose 'Whole dataset' mode.", category="warning")
            return redirect(url_for(f"map_center.map_by_{option}"))

        if option == "country":

            boundaries = None
            country_code = form.country.data
            default_location = get_country_centroid(form.country.data)
            success_message = f"country={get_country_name(country_code)}"
        else:
            boundaries = {
                "lon_min": form.lon_min.data,
                "lon_max": form.lon_max.data,
                "lat_min": form.lat_min.data,
                "lat_max": form.lat_max.data
            }
            default_location = generate_coordinates_center(**boundaries)
            country_code = None
        zoom_value = int(form.zoom.data)
        order = int(form.interpolation_type.data)
        try:
            final_boundaries = create_files_for_choropleths_with_interpolation_get_boundaries(dataset_hash=dataset_hash,
                                                                                              boundaries=boundaries,
                                                                                              order=order,
                                                                                              zoom_value=zoom_value,
                                                                                              country_code=country_code)
        except NoChosenCoordsInDatasetException:
            if "m" in globals():
                del m
            flash(f"No values were found for chosen {option}", category="warning")
            return redirect(url_for(f"map_center.map_by_{option}"))
    else:
        create_files_for_choropleths_whole_dataset(dataset_hash)
        final_boundaries = get_boundary_values_for_dataset(dataset_hash)
        default_location = generate_coordinates_center(**final_boundaries)

    if option in ("coordinates", "whole_dataset"):
        coordinates_str = f"Longitude=({final_boundaries['lon_min']}, {final_boundaries['lon_max']}), " \
                          f"Latitude=({final_boundaries['lat_min']}, {final_boundaries['lat_max']})"
        success_message = f"Coordinates=[{coordinates_str}]"

    if option in ("coordinates", "country"):
        interpolation_name = dict(form.interpolation_type.choices).get(int(form.interpolation_type.data))
        zoom_name = dict(form.zoom.choices).get(int(form.zoom.data))
        success_message = f"{success_message}, Zoom={zoom_name}, Interpolation={interpolation_name}"

    m = MapCreator(fill_color=fill_color,
                   fill_opacity=fill_opacity,
                   line_opacity=line_opacity,
                   default_location=default_location).map
    flash(f"Map generated for {success_message}.", category="success")


def create_files_for_choropleths_with_interpolation_get_boundaries(dataset_hash: str, zoom_value: int, order: int,
                                                                   boundaries: dict = None, country_code: str = None)\
                                                                   -> dict:
    row_data, lon_resolution, lat_resolution, bounding_box = prepare_data_for_interpolation(dataset_hash, country_code)
    interpolator = Interpolator(row_data, lon_resolution, bounding_box=bounding_box,
                                chosen_boundary_coordinates=boundaries)
    interpolated_coordinates, interpolated_values = interpolator.interpolate(zoom_value, order)

    map_files_creator = DataFilesCreator(interpolated_coordinates, interpolated_values, lon_resolution, lat_resolution,
                                         zoom_value, country_code)
    map_files_creator.create_files()
    return interpolator.boundaries


def prepare_data_for_interpolation(dataset_hash: str, country_code: str = None):
    row_data = get_dataset(dataset_hash)
    metadata = get_data_metadata(dataset_hash)
    lon_resolution, lat_resolution = metadata.lon_resolution, metadata.lat_resolution
    bounding_box = get_country_bounding_box(country_code) if country_code else None
    return row_data, lon_resolution, lat_resolution, bounding_box


def create_files_for_choropleths_whole_dataset(dataset_hash: str):
    row_data, lon_resolution, lat_resolution, _ = prepare_data_for_interpolation(dataset_hash)

    map_files_creator = DataFilesCreator([list(row[:2]) for row in row_data],
                                         [row[2] for row in row_data],
                                         lon_resolution, lat_resolution, zoom_value=1, country_code=None)
    map_files_creator.create_files()
