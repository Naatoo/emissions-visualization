import os
from pathlib import Path


MAIN_DIR = str(Path(__file__).parent.parent)
DATA_DIR = os.path.join(MAIN_DIR, "data_center/")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw/")
OUTPUT_DATA_DIR = os.path.join(DATA_DIR, "output/")
PM10_RAW_FILE = os.path.join(RAW_DATA_DIR, "PM10_raw.txt")
PM10_JSON_FILE = os.path.join(OUTPUT_DATA_DIR, "PM10_zoomed.json")
PM10_CSV_FILE = os.path.join(OUTPUT_DATA_DIR, "PM10_zoomed.csv")
EMISSION_EXCEL_FILE = os.path.join(RAW_DATA_DIR, 'emission.xlsx')
COUNTRIES_TXT_FILE = os.path.join(RAW_DATA_DIR, 'countries.txt')
BOUNDING_BOXES_JSON = os.path.join(RAW_DATA_DIR, 'bounding_boxes.json')
COUNTRIES_CENTROIDS_CSV = os.path.join(RAW_DATA_DIR, "countries_centroids.csv")
