from flask import redirect, url_for

from . import home


@home.route('/')
def homepage():
    """
    Redirect to /login
    """
    return redirect(url_for('data_center_select.choose_data'))
