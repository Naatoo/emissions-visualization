from app.database.database import db


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
