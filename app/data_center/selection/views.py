from flask import render_template, redirect, url_for, request, flash
from flask import current_app as app
from flask_login import login_required

from app.data_center.selection import data_center_select
from app.database.queries import delete_data, get_data_metadata, get_selected_data_str
from app.models.dataset import DatasetInfo


@data_center_select.route('/data_center/select', methods=['GET', 'POST'])
@login_required
def choose_data():
    delete_data = {}
    delete_hash = request.args.get('delete_hash')
    if delete_hash:
        metadata = get_data_metadata(delete_hash)
        delete_str = f"Are you sure you want to delete {metadata.name}, {metadata.physical_quantity}, {metadata.year}"
        delete_data.update({
            "delete_hash": delete_hash,
            "delete_str": delete_str
        })
    data = DatasetInfo.query.all()
    table_data = [[row.dataset_hash, row.name, row.compound, row.physical_quantity,
                   row.unit, row.year, row.lon_resolution, row.lat_resolution, row.relative_data] for row in data]
    dataset_hash = app.config.get('CURRENT_DATA_HASH')
    selected_data_str = get_selected_data_str()
    return render_template("data_center_select.html", rows=table_data, current_hash=dataset_hash,
                           selected_data_str=selected_data_str, **delete_data)


@data_center_select.route('/data_center/select/<string:value>', methods=['GET', 'POST'])
@login_required
def select(value):
    app.config['CURRENT_DATA_HASH'] = value
    return redirect(url_for("data_center_select.choose_data"))


@data_center_select.route('/data_center/delete/<string:value>', methods=['GET', 'POST'])
@login_required
def delete(value):
    # TODO set default data hash
    return redirect(url_for("data_center_select.choose_data", delete_hash=value))


@data_center_select.route('/data_center/delete/<string:value>/confirm', methods=['GET', 'POST'])
@login_required
def confirm_delete(value):
    # TODO set default data hash
    metadata = get_data_metadata(value)
    flash(f"DELETED: Data {metadata.name} of {metadata.physical_quantity} from year {metadata.year}.", category='info')
    delete_data(value)
    if app.config.get('CURRENT_DATA_HASH') == value:
        del app.config['CURRENT_DATA_HASH']
    return redirect(url_for("data_center_select.choose_data"))
