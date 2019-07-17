from flask import Flask

from flask_bootstrap import Bootstrap
import os

from app.database.initial_data_insertion import insert_countries_data
from .home import home as home_blueprint
from .data_center.selection import data_center_select as data_center_select_blueprint
from .data_center.add_data import data_center_add_data as data_center_add_data_blueprint
from .data_center.upload_file import data_center_upload_file as data_center_upload_file_blueprint
from .map_center import map_center as map_center_blueprint
from app.map_center.views import generate_map_by_coordinates, generate_map_by_country
from app.database.database import db

from .data_center.loader.excel_parser import ExcelFileParser
from .data_center.loader.emep_txt_parser import EmepTxtFileParser
from app.tools.paths import EUROPE_EMISSION_PM10_2015_EXCEL_FILE, COUNTRIES_CENTROIDS_CSV, PM10_RAW_FILE
from app.models.data_models import DatasetValues, DatasetInfo
from app.tools.paths import DATABASE_FILE

import secrets


def create_app():
    app = Flask(__name__)
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE_FILE}"
    Bootstrap(app)
    db.init_app(app)
    app.register_blueprint(home_blueprint)
    app.register_blueprint(data_center_select_blueprint)
    app.register_blueprint(data_center_upload_file_blueprint)
    app.register_blueprint(data_center_add_data_blueprint)
    app.register_blueprint(map_center_blueprint)
    return app


def setup_database(app):
    with app.app_context():
        db.create_all()
        # insert_initial_europe_data()
        # insert_initial_emep_data()
        # insert_countries_data()


def insert_initial_europe_data():
    dataset_hash = secrets.token_hex(nbytes=16)
    name = "normal"
    compound = 'PM10'
    physical_quantity = "concentration"
    unit = 'µg/m3'
    year = 2015
    parser = ExcelFileParser(file_name=EUROPE_EMISSION_PM10_2015_EXCEL_FILE)
    db.session.add(DatasetInfo(
        dataset_hash=dataset_hash,
        name=name,
        compound=compound,
        physical_quantity=physical_quantity,
        unit=unit,
        year=year,
    ))
    db.session.commit()
    for (lon, lat, value) in parser.parse_data_file():
        db.session.add(DatasetValues(dataset_hash=dataset_hash,
                                     lon=lon,
                                     lat=lat,
                                     value=value
                                     ))
        db.session.flush()
    db.session.commit()


def insert_initial_emep_data():
    dataset_hash = secrets.token_hex(nbytes=4)
    physical_quantity = "emission"
    year = 2015
    name = "PM10 yearly"
    parser = EmepTxtFileParser(file_name=PM10_RAW_FILE)

    db.session.add(DatasetInfo(
        dataset_hash=dataset_hash,
        physical_quantity=physical_quantity,
        year=year,
        name=name
    ))
    for (lon, lat, value) in parser.parse_data_file():
        db.session.add(DatasetValues(dataset_hash=dataset_hash,
                                     lon=lon,
                                     lat=lat,
                                     value=value
                                     ))
        # db.session.flush()
    db.session.commit()
