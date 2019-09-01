import os

from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from app.data_center.loader.emep_txt_parser import EmepTxtFileParser
from app.data_center.loader.excel_parser import ExcelFileParser
from app.data_center.add_data import data_center_add_data
from app.data_center.add_data.forms import AddDataForm
from app.database.queries import insert_new_file_data, get_selected_data_str
from app.tools.paths import UPLOADED_FILE_DIR


@data_center_add_data.route('/data_center/add_data', methods=['GET', 'POST'])
@login_required
def add_data():
    filename = next(file for file in os.listdir(UPLOADED_FILE_DIR))
    parsers_mapping = {
        "xlsx": ExcelFileParser,
        "txt": EmepTxtFileParser
    }
    file_type = filename.split(".")[1]
    parser = parsers_mapping[file_type](f'{UPLOADED_FILE_DIR}/{filename}')
    preview_data = parser.get_data_for_preview(limit=20)
    form = AddDataForm()
    if form.is_submitted():
        name = form.name.data
        compound = form.compound.data
        physical_quantity = form.physical_quantity.data
        unit = form.unit.data
        year = form.year.data
        lon_resolution = form.lon_resolution.data
        lat_resolution = form.lat_resolution.data
        relative_data = True if int(form.relative_data.data) else False
        metadata = {
            "name": name,
            "compound": compound,
            "physical_quantity": physical_quantity,
            "unit": unit,
            "year": year,
            "lon_resolution": lon_resolution,
            "lat_resolution": lat_resolution,
            "relative_data": relative_data
        }
        try:
            float(lon_resolution)
            float(lat_resolution)
        except ValueError:
            flash("Longitude and latitude resolution must be numbers.", category='warning')
            return redirect(url_for("data_center_upload_file.upload_file"))
        insert_new_file_data(parser, **metadata)
        flash(f"Dataset {name}, {compound}, {physical_quantity}, {year} was added.", category='success')
        return redirect(url_for("data_center_upload_file.upload_file"))
    selected_data_str = get_selected_data_str()
    return render_template("data_center_add_data.html", form=form,
                           selected_data_str=selected_data_str, preview_data=preview_data)



