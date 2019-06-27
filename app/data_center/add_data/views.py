from flask import render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

from app.data_center.add_data import data_center_add_data
from app.data_center.add_data.forms import AddDataForm
from app.database.queries import insert_new_file_data, get_selected_data_str
from app.tools.paths import TEMP_DIR


@data_center_add_data.route('/data_center/add_data', methods=['GET', 'POST'])
def add_data():
    form = AddDataForm()
    if form.is_submitted():
        #TODO validators

        name = form.name.data
        physical_quantity = form.physical_quantity.data
        year = form.year.data
        metadata = {
            "name": name,
            "physical_quantity": physical_quantity,
            "year": year
        }
        insert_new_file_data(**metadata)
        flash(f"ADDED: {name} of {physical_quantity} from year {year}.", category='success')
        return redirect(url_for("data_center_upload_file.upload_file"))
    selected_data_str = get_selected_data_str()
    return render_template("data_center_add_data.html", form=form, selected_data_str=selected_data_str)



