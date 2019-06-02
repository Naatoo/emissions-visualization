from flask import render_template, redirect, url_for

from app.data_center.selection import data_center
from app.data_center.selection.forms import DataSourceForm


@data_center.route('/data_center/select', methods=['GET', 'POST'])
def choose_data():
    form = DataSourceForm()
    if form.is_submitted():
        source = form.source.data
        # TODO rest of the fields
        return redirect(url_for("data_source.choose_data"))
    return render_template("data_source.html", form=form)

