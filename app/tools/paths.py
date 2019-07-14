import os
from pathlib import Path


MAIN_DIR = str(Path(__file__).parent.parent)

DATA_DIR = os.path.join(MAIN_DIR, "data_center/")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw/")
OUTPUT_DATA_DIR = os.path.join(DATA_DIR, "output/")
PM10_RAW_FILE = os.path.join(RAW_DATA_DIR, "PM10_raw.txt")

COORDINATES_FILE = os.path.join(OUTPUT_DATA_DIR, "coordinates.json")
VALUES_FILE = os.path.join(OUTPUT_DATA_DIR, "values.csv")

EUROPE_EMISSION_PM25_2015_EXCEL_FILE = os.path.join(RAW_DATA_DIR, 'europe_PM25_2015.xlsx')
EUROPE_EMISSION_PM10_2015_EXCEL_FILE = os.path.join(RAW_DATA_DIR, 'europe_PM10_2015.xlsx')

COUNTRIES_TXT_FILE = os.path.join(RAW_DATA_DIR, 'countries.txt')
BOUNDING_BOXES_JSON = os.path.join(RAW_DATA_DIR, 'bounding_boxes.json')
COUNTRIES_CENTROIDS_CSV = os.path.join(RAW_DATA_DIR, "countries_centroids.csv")

DATABASE_DIR = os.path.join(MAIN_DIR, "database/")
DATABASE_FILE = os.path.join(DATABASE_DIR, "data.db")

TEMP_DIR = os.path.join(MAIN_DIR, "temp/")
UPLOADED_FILE = os.path.join(TEMP_DIR, "uploaded_file")
