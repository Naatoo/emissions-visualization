from flask import Blueprint

data_center_add_data = Blueprint('data_center_add_data', __name__)

from app.data_center.add_data import views
