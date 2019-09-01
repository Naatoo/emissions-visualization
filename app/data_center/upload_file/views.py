from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.data_center.loader.emep_txt_parser import EmepTxtFileParser
from app.data_center.loader.excel_parser import ExcelFileParser
from app.data_center.upload_file import data_center_upload_file
from app.data_center.upload_file.forms import UploadFileForm
from app.database.queries import get_selected_data_str
from app.tools.paths import UPLOADED_FILE


@data_center_upload_file.route('/data_center/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = UploadFileForm()
    if form.is_submitted():
        filename = secure_filename(form.file.data.filename)
        possible_extensions = {"xlsx": "xlsx", "emep": "txt"}
        form.file.data.save(UPLOADED_FILE)
        file_type = form.file_type.data
        error_msg = None
        if not filename.endswith(possible_extensions[file_type]):
            error_msg = f"{filename} has other extension than expected for this file type: {file_type}."
        elif not validate_file_coordinates_unique(filename):
            error_msg = f"{filename} has non-unique coordinates."
        if error_msg is not None:
            flash(error_msg, category="danger")
            return render_template("data_center_upload_file.html", form=form, selected_data_str=get_selected_data_str())
        else:
            return redirect(url_for("data_center_add_data.add_data", file_type=file_type))

    return render_template("data_center_upload_file.html", form=form, selected_data_str=get_selected_data_str())


def validate_file_coordinates_unique(filename: str) -> bool:
    extension = filename.split(".")[1]
    parsers_mapping = {
        "xlsx": ExcelFileParser,
        "emep": EmepTxtFileParser
    }
    rows_len = len(list(parsers_mapping[extension](UPLOADED_FILE).rows_generator()))
    unique_rows_len = len(list(set(tup[:2] for tup in parsers_mapping[extension](UPLOADED_FILE).rows_generator())))
    return rows_len == unique_rows_len
