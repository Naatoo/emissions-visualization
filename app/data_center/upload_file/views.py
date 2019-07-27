from flask import render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

from app.data_center.upload_file import data_center_upload_file
from app.data_center.upload_file.forms import UploadFileForm
from app.database.queries import get_selected_data_str
from app.tools.paths import UPLOADED_FILE


@data_center_upload_file.route('/data_center/upload_file', methods=['GET', 'POST'])
def upload_file():
    form = UploadFileForm()
    if form.is_submitted():
        filename = secure_filename(form.file.data.filename)
        possible_extensions = "xlsx", "json", "txt", "csv"
        form.file.data.save(UPLOADED_FILE)
        if filename.endswith(possible_extensions):
            correct = True
        else:
            correct = False
            error_msg = f"{filename} has other extension then possible: {possible_extensions}"
        if correct:
            return redirect(url_for("data_center_add_data.add_data", file_type=form.file_type.data))
        else:
            flash(error_msg, category="danger")
            return render_template("data_center_upload_file.html", form=form, selected_data_str=get_selected_data_str())
    return render_template("data_center_upload_file.html", form=form, selected_data_str=get_selected_data_str())

#TODO add file validators
