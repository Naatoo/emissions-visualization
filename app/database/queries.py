import secrets
from flask import current_app as app

from app.database.database import db
from app.models.data_models import DataInfo, DataValues
from app.tools.paths import UPLOADED_FILE
from app.data_center.loader.excel_parser import ExcelFileParser


def insert_new_file_data(**kwargs):
    dataset_hash = secrets.token_hex(nbytes=16)
    parser = ExcelFileParser(UPLOADED_FILE)
    db.session.add(DataInfo(
        dataset_hash=dataset_hash,
        physical_quantity=kwargs["physical_quantity"],
        year=kwargs["year"],
        name=kwargs["name"]
    ))
    db.session.commit()
    for (lon, lat, value) in parser.parse_data_file():
        db.session.add(DataValues(dataset_hash=dataset_hash,
                                  lon=lon,
                                  lat=lat,
                                  value=value
                                  ))
        db.session.flush()
    db.session.commit()


def delete_data(dataset_hash):
    db.session.delete(DataInfo.query.filter_by(dataset_hash=dataset_hash).one())
    db.session.commit()
    for row in DataValues.query.filter_by(dataset_hash=dataset_hash).all():
        db.session.delete(row)
        db.session.flush()
    db.session.commit()


def get_dataset(dataset_hash, rows_limit: int=None):
    dataset = DataValues.query.filter_by(dataset_hash=dataset_hash)
    if rows_limit:
        dataset = dataset.limit(rows_limit)
    return [(row.lon, row.lat, row.value) for row in dataset.all()]


def get_data_metadata(dataset_hash):
    data = DataInfo.query.filter_by(dataset_hash=dataset_hash).one()
    return data


def get_selected_data_str():
    dataset_hash = app.config.get('CURRENT_DATA_HASH')
    if dataset_hash:
        metadata = get_data_metadata(dataset_hash)
        selected_data_str = f"{metadata.name}, {metadata.physical_quantity}, {metadata.year}"
    else:
        selected_data_str = None
    return selected_data_str


def get_hash_of_first_dataset():
    return DataInfo.query.all()[0].dataset_hash
