from flask import Blueprint

map_center = Blueprint('map_center', __name__)

from app.map_center import views
