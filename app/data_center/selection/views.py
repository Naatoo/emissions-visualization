from flask import render_template, redirect, url_for, request, flash
from flask import current_app as app

from app.data_center.selection import data_center_select
from app.database.queries import delete_data, get_data_metadata, get_selected_data_str
from app.models.emission_data import DataInfo


@data_center_select.route('/data_center/select', methods=['GET', 'POST'])
def choose_data():
    data = DataInfo.query.all()
    table_data = [[row.name, row.year, row.physical_quantity, row.dataset_hash] for row in data]
    dataset_hash = app.config.get('CURRENT_DATA_HASH')
    selected_data_str = get_selected_data_str()
    return render_template("data_center_select.html", rows=table_data, current_hash=dataset_hash,
                           selected_data_str=selected_data_str)


@data_center_select.route('/data_center/select/<string:value>', methods=['GET', 'POST'])
def select(value):
    app.config['CURRENT_DATA_HASH'] = value
    metadata = get_data_metadata(value)
    # flash(f"SELECTED: Data {metadata.name} of {metadata.physical_quantity} from year {metadata.year}.")
    return redirect(url_for("data_center_select.choose_data"))


@data_center_select.route('/data_center/delete/<string:value>', methods=['GET', 'POST'])
def delete(value):
    # TODO set default data hash
    metadata = get_data_metadata(value)
    flash(f"DELETED: Data {metadata.name} of {metadata.physical_quantity} from year {metadata.year}.")
    delete_data(value)
    if app.config.get('CURRENT_DATA_HASH') == value:
        del app.config['CURRENT_DATA_HASH']
    return redirect(url_for("data_center_select.choose_data"))
