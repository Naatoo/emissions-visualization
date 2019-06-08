from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired


class DataSourceForm(FlaskForm):
    """
    Form for users to add new energy bill
    """
    # TODO add more fields
    submit = SubmitField('Submit')
