from sqlalchemy import UniqueConstraint

from app.database.database import db


class DataValues(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_hash = db.Column(db.Unicode)
    lon = db.Column(db.Float)
    lat = db.Column(db.Float)
    value = db.Column(db.Float)
    

class DataInfo(db.Model):
    dataset_hash = db.Column(db.Unicode, primary_key=True)
    physical_quantity = db.Column(db.String)
    name = db.Column(db.String)
    year = db.Column(db.Integer)
    __table_args__ = (UniqueConstraint('physical_quantity', 'name', 'year', name='dataset_info'),
                      )


