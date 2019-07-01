from flask import Blueprint

data_center_upload_file = Blueprint('data_center_upload_file', __name__)

from app.data_center.upload_file import views
