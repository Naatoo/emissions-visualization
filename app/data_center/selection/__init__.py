from flask import Blueprint

data_center_select = Blueprint('data_center_select', __name__)

from app.data_center.selection import views
