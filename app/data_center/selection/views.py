from flask import render_template, redirect, url_for, request
from flask import current_app as app

from app.data_center.selection import data_center_select
from app.data_center.selection.forms import DataSourceForm
from app.database.queries import delete_data
from app.models.emission_data import DataInfo


@data_center_select.route('/data_center/select', methods=['GET', 'POST'])
def choose_data():
    data = DataInfo.query.all()
    table_data = [[row.name, row.year, row.physical_quantity, row.dataset_hash] for row in data]
    return render_template("data_center_select.html", form=form, rows=table_data)


@data_center_select.route('/data_center/select/<string:value>', methods=['GET', 'POST'])
def select(value):
    app.config['CURRENT_DATA_HASH'] = value
    return redirect(url_for("data_center_select.choose_data"))


@data_center_select.route('/data_center/delete/<string:value>', methods=['GET', 'POST'])
def delete(value):
    # TODO set default data hash
    delete_data(value)
    return redirect(url_for("data_center_select.choose_data"))
