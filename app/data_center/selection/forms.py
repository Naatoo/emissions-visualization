from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired


class DataSourceForm(FlaskForm):
    """
    Form for users to add new energy bill
    """
    source = SelectField('Data source', validators=[DataRequired()], choices=[("emep", "EMEP"), ("another", "Another")],
                         default="emep")
    # TODO add more fields
    submit = SubmitField('Refresh')
