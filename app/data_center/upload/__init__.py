from flask import Blueprint

data_center_upload = Blueprint('data_center_upload', __name__)

from app.data_center.upload import views
