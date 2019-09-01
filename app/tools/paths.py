import os
from pathlib import Path


MAIN_DIR = str(Path(__file__).parent.parent)

DATABASE_DIR = os.path.join(MAIN_DIR, "database/")
DATABASE_FILE = os.path.join(DATABASE_DIR, "data.db")

COUNTRIES_DATA_DIR = os.path.join(DATABASE_DIR, "countries_data/")
COUNTRIES_TXT_FILE = os.path.join(COUNTRIES_DATA_DIR, 'countries.txt')
BOUNDING_BOXES_JSON = os.path.join(COUNTRIES_DATA_DIR, 'bounding_boxes.json')
COUNTRIES_CENTROIDS_CSV = os.path.join(COUNTRIES_DATA_DIR, "countries_centroids.csv")

INITIAL_DATA_DIR = os.path.join(DATABASE_DIR, "initial_data/")
EUROPE_EMISSION_PM25_2015_EXCEL_FILE = os.path.join(INITIAL_DATA_DIR, 'europe_PM25_2015.xlsx')
EUROPE_EMISSION_PM10_2015_EXCEL_FILE = os.path.join(INITIAL_DATA_DIR, 'europe_PM10_2015.xlsx')
PM10_RAW_FILE = os.path.join(INITIAL_DATA_DIR, "PM10_raw.txt")

MAP_CENTER_DIR = os.path.join(MAIN_DIR, "map_center/")
TEMP_MAP_CENTER_DIR = os.path.join(MAP_CENTER_DIR, "temp/")
COORDINATES_FILE = os.path.join(TEMP_MAP_CENTER_DIR, "coordinates.json")
VALUES_FILE = os.path.join(TEMP_MAP_CENTER_DIR, "values.csv")

UPLOADED_FILE_DIR = os.path.join(MAIN_DIR, "data_center/upload_file/temp")
