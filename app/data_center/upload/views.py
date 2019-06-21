from flask import render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

from app.data_center.upload import data_center_upload
from app.data_center.upload.forms import DataUploadForm
from app.database.queries import insert_new_file_data, get_selected_data_str
from app.tools.paths import TEMP_DIR


@data_center_upload.route('/data_center/upload', methods=['GET', 'POST'])
def upload_data():
    form = DataUploadForm()
    if form.is_submitted():
        filename = secure_filename(form.file.data.filename)
        #TODO validators

        form.file.data.save(TEMP_DIR + "uploaded_file")

        name = form.name.data
        physical_quantity = form.physical_quantity.data
        year = form.year.data
        metadata = {
            "name": name,
            "physical_quantity": physical_quantity,
            "year": year
        }
        insert_new_file_data(**metadata)
        flash(f"ADDED: {name} of {physical_quantity} from year {year}.")
        return redirect(url_for("data_center_upload.upload_data"))
    selected_data_str = get_selected_data_str()
    return render_template("data_center_upload.html", form=form, selected_data_str=selected_data_str)



