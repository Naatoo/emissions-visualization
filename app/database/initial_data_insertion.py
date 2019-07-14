import pandas
import json

from app.database.database import db
from app.models.data_models import Countries

from app.tools.paths import COUNTRIES_CENTROIDS_CSV, BOUNDING_BOXES_JSON


def insert_countries_data():
    if not Countries.query.all():
        for code, name, [box_lon_min, box_lat_min, box_lon_max, box_lat_max] in get_country_code_name_bounding_box():
            print(code, name, [box_lon_min, box_lat_min, box_lon_max, box_lat_max])
            try:
                centroid_lon, centroid_lat = get_country_centroid(code)
            except TypeError:
                continue
            db.session.add(Countries(code=code,
                                     name=name,
                                     centroid_lon=centroid_lon,
                                     centroid_lat=centroid_lat,
                                     box_lon_min=box_lon_min,
                                     box_lat_min=box_lat_min,
                                     box_lon_max=box_lon_max,
                                     box_lat_max=box_lat_max
                                     ))
            db.session.commit()


def get_country_centroid(code: str):
    data = pandas.read_csv(COUNTRIES_CENTROIDS_CSV)
    for lon, lat, country_code in zip(data['lon'], data['lat'], data['code']):
        if code == country_code:
            return lon, lat


def get_country_code_name_bounding_box():
    with open(BOUNDING_BOXES_JSON) as file:
        data = json.load(file)
        for code in data:
            yield (code, *data[code])


get_country_code_name_bounding_box()
