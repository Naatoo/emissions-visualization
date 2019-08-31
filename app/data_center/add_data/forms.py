from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, DecimalField
from wtforms.validators import DataRequired


class AddDataForm(FlaskForm):
    """
    Form for adding new file with description
    """
    # TODO add more fields
    name = StringField('Name', validators=[DataRequired()])
    compound = StringField('Compound', validators=[DataRequired()])
    physical_quantity = StringField('Physical quantity', validators=[DataRequired()])
    unit = StringField('Unit', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    lon_resolution = DecimalField('Longitude resolution', validators=[DataRequired()])
    lat_resolution = DecimalField('Latitude resolution', validators=[DataRequired()])
    relative_data = SelectField('Relative data', validators=[DataRequired()], choices=[(1, 'Yes'), (0, 'No')],
                                default=1)
    submit = SubmitField('Submit')
