from flask import Blueprint

data_center = Blueprint('data_center', __name__)

from app.data_center.selection import views
