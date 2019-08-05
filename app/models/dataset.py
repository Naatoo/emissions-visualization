from sqlalchemy import UniqueConstraint, ForeignKey

from app.database.database import db


class DatasetValues(db.Model):
    __tablename__ = 'data_values'
    id = db.Column(db.Integer, primary_key=True)
    dataset_hash = db.Column(db.String(32), FaoreignKey('data_info.dataset_hash'))
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
    lon_resolution = db.Column(db.Float)
    lat_resolution = db.Column(db.Float)
    __table_args__ = (UniqueConstraint('compound', 'physical_quantity', 'name', 'year', name='dataset_info'),)
