import secrets

from flask import current_app as app
from sqlalchemy import and_

from app.database.database import db
from app.models.data_models import DatasetInfo, DatasetValues, Countries


def insert_new_file_data(parser, **kwargs):
    dataset_hash = secrets.token_hex(nbytes=16)
    db.session.add(DatasetInfo(
        dataset_hash=dataset_hash,
        physical_quantity=kwargs["physical_quantity"],
        year=kwargs["year"],
        name=kwargs["name"],
        grid_resolution=kwargs["grid_resolution"]
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


def get_selected_data_str():
    dataset_hash = app.config.get('CURRENT_DATA_HASH')
    if dataset_hash:
        metadata = get_data_metadata(dataset_hash)
        selected_data_str = f"{metadata.name}, {metadata.physical_quantity}, {metadata.year}"
    else:
        selected_data_str = None
    return selected_data_str


def get_hash_of_first_dataset():
    return DatasetInfo.query.all()[0].dataset_hash
