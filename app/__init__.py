from flask import Flask

from flask_bootstrap import Bootstrap
import os

from app.database.initial_data_insertion import insert_countries_data
from .home import home as home_blueprint
from .data_center.selection import data_center_select as data_center_select_blueprint
from .data_center.add_data import data_center_add_data as data_center_add_data_blueprint
from .data_center.upload_file import data_center_upload_file as data_center_upload_file_blueprint
from .map_center import map_center as map_center_blueprint
from app.database.database import db

from .data_center.loader.excel_parser import ExcelFileParser
from .data_center.loader.emep_txt_parser import EmepTxtFileParser
from app.tools.paths import EUROPE_EMISSION_PM10_2015_EXCEL_FILE, COUNTRIES_CENTROIDS_CSV, PM10_RAW_FILE
from app.models.data_models import DatasetValues, DatasetInfo
from app.tools.paths import DATABASE_FILE


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
        # insert_countries_data()
