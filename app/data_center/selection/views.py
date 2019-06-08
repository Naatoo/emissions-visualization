from flask import render_template, redirect, url_for, request
from flask import current_app as app

from app.data_center.selection import data_center
from app.data_center.selection.forms import DataSourceForm
from app.models.emission_data import DataInfo


@data_center.route('/data_center/select', methods=['GET', 'POST'])
def choose_data():
    data = DataInfo.query.all()
    table_data = [[row.name, row.year, row.physical_quantity, row.dataset_hash] for row in data]
    form = DataSourceForm()
    if form.is_submitted():
        dataset_hash = request.form["chosen_data"]
        app.config['CURRENT_DATA_HASH'] = dataset_hash
        return redirect(url_for("data_center.choose_data"))
    return render_template("data_center_select.html", form=form, rows=table_data)

