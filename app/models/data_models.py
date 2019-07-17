from sqlalchemy import UniqueConstraint, ForeignKey

from app.database.database import db


class DatasetValues(db.Model):
    __tablename__ = 'data_values'
    id = db.Column(db.Integer, primary_key=True)
    dataset_hash = db.Column(db.String(32), ForeignKey('data_info.dataset_hash'))
    lon = db.Column(db.Float)
    lat = db.Column(db.Float)
    value = db.Column(db.Float)
    

class DatasetInfo(db.Model):
    __tablename__ = 'data_info'
    dataset_hash = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    compound = db.Column(db.String(30))
    physical_quantity = db.Column(db.String(20))
    unit = db.Column(db.String(10))
    year = db.Column(db.SmallInteger)
    grid_resolution = db.Column(db.Float)
    __table_args__ = (UniqueConstraint('compound', 'physical_quantity', 'name', 'year', name='dataset_info'),)


class Countries(db.Model):
    __tablename__ = 'countries'
    code = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.String(50))
    centroid_lon = db.Column(db.Float)
    centroid_lat = db.Column(db.Float)
    box_lon_min = db.Column(db.Float)
    box_lon_max = db.Column(db.Float)
    box_lat_min = db.Column(db.Float)
    box_lat_max = db.Column(db.Float)
