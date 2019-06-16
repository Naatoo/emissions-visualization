import secrets

from app.database.database import db
from app.models.emission_data import DataInfo, DataValues
from app.tools.paths import TEMP_DIR
from app.data_center.loader.excel_parser import ExcelFileParser


def insert_new_file_data(**kwargs):
    dataset_hash = secrets.token_hex(nbytes=4)
    parser = ExcelFileParser(file_name=TEMP_DIR + "uploaded_file")
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

