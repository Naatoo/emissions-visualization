import secrets

from flask import current_app as app
from sqlalchemy import and_

from app.database.database import db
from app.models.dataset import DatasetInfo, DatasetValues
from app.models.countries import Countries
from app.models.auth import User
from app.tools.exceptions import LonLatResolutionException, ZoomingRelativeDataException


def insert_new_file_data(parser, **kwargs):
    dataset_hash = secrets.token_hex(nbytes=16)
    db.session.add(DatasetInfo(
        dataset_hash=dataset_hash,
        compound=kwargs["compound"],
        physical_quantity=kwargs["physical_quantity"],
        unit=kwargs["unit"],
        year=kwargs["year"],
        name=kwargs["name"],
        lon_resolution=kwargs["lon_resolution"],
        lat_resolution=kwargs["lat_resolution"],
        relative_data=kwargs["relative_data"],
    ))
    db.session.commit()
    for (lon, lat, value) in parser.rows_generator():
        db.session.add(DatasetValues(dataset_hash=dataset_hash,
                                     lon=lon,
                                     lat=lat,
                                     value=value
                                     ))
        db.session.flush()
    db.session.commit()


def delete_data(dataset_hash):
    db.session.delete(DatasetInfo.query.filter_by(dataset_hash=dataset_hash).one())
    db.session.commit()
    for row in DatasetValues.query.filter_by(dataset_hash=dataset_hash).all():
        db.session.delete(row)
        db.session.flush()
    db.session.commit()


def get_dataset(dataset_hash, rows_limit: int=None):
    dataset = DatasetValues.query.filter_by(dataset_hash=dataset_hash)
    if rows_limit:
        dataset = dataset.limit(rows_limit)
    return [(row.lon, row.lat, row.value) for row in dataset.all()]


def get_dataset_by_coordinates(dataset_hash, boundary_coordinates: dict):
    dataset = DatasetValues.query.filter_by(and_(dataset_hash=dataset_hash, **boundary_coordinates))
    return [(row.lon, row.lat, row.value) for row in dataset.all()]


def get_data_metadata(dataset_hash):
    data = DatasetInfo.query.filter_by(dataset_hash=dataset_hash).one()
    return data


def get_country_bounding_box(code: str) -> tuple:
    data = Countries.query.filter_by(code=code).one()
    return data.box_lon_min, data.box_lon_max, data.box_lat_min, data.box_lat_max


def get_country_centroid(code: str) -> tuple:
    data = Countries.query.filter_by(code=code).one()
    return data.centroid_lat, data.centroid_lon


def get_country_name(code: str) -> str:
    data = Countries.query.filter_by(code=code).one()
    return data.name


def get_selected_data_str():
    dataset_hash = app.config.get('CURRENT_DATA_HASH')
    if dataset_hash:
        metadata = get_data_metadata(dataset_hash)
        boundary_values = get_boundary_values_for_dataset(dataset_hash)
        selected_data_str = f"{metadata.name}, {metadata.physical_quantity}, " \
                            f" {metadata.compound}, {metadata.unit}, {metadata.year}, " \
                            f"Longitude=({boundary_values['lon_min']}, {boundary_values['lon_max']}), " \
                            f"Latitude=({boundary_values['lat_min']},{boundary_values['lat_max']})"
    else:
        selected_data_str = "No data selected"
    return selected_data_str


def assert_lon_lat_resolution_identical(dataset_hash):
    data = get_data_metadata(dataset_hash)
    if float(data.lon_resolution) != float(data.lat_resolution):
        raise LonLatResolutionException


def assert_zooming_relative_data(dataset_hash, zoom_value: int):
    data = get_data_metadata(dataset_hash)
    if zoom_value != 0 and data.relative_data is False:
        raise ZoomingRelativeDataException


def get_boundary_values_for_dataset(dataset_hash: str) -> dict:
    lon_min = DatasetValues.query.filter_by(dataset_hash=dataset_hash).order_by(DatasetValues.lon).first().lon
    lon_max = DatasetValues.query.filter_by(dataset_hash=dataset_hash).order_by(DatasetValues.lon.desc()).first().lon
    lat_min = DatasetValues.query.filter_by(dataset_hash=dataset_hash).order_by(DatasetValues.lat).first().lat
    lat_max = DatasetValues.query.filter_by(dataset_hash=dataset_hash).order_by(DatasetValues.lat.desc()).first().lat
    return {"lon_min": lon_min, "lon_max": lon_max, "lat_min": lat_min, "lat_max": lat_max}


def get_user(username: str):
    user = User.query.filter_by(username=username).first()
    return user

#
# def insert_user(username, password):
#     db.session.add(User(username=username, password=password))
#     db.session.commit()
