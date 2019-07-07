from flask import render_template, redirect, url_for, flash

from app.data_center.loader.emep_txt_parser import EmepTxtFileParser
from app.data_center.loader.excel_parser import ExcelFileParser
from app.data_center.add_data import data_center_add_data
from app.data_center.add_data.forms import AddDataForm
from app.database.queries import insert_new_file_data, get_selected_data_str
from app.tools.paths import UPLOADED_FILE


@data_center_add_data.route('/data_center/add_data/<string:file_type>', methods=['GET', 'POST'])
def add_data(file_type):
    parsers_mapping = {
        "xlsx": ExcelFileParser,
        "emep": EmepTxtFileParser
    }
    parser = parsers_mapping[file_type](UPLOADED_FILE)
    preview_data = parser.get_data_for_preview(limit=20)
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
        insert_new_file_data(parser, **metadata)
        flash(f"ADDED: {name} of {physical_quantity} from year {year}.", category='success')
        return redirect(url_for("data_center_upload_file.upload_file"))
    selected_data_str = get_selected_data_str()
    return render_template("data_center_add_data.html", form=form,
                           selected_data_str=selected_data_str, preview_data=preview_data)



