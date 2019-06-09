from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, StringField, SelectField
from wtforms.validators import DataRequired


class DataUploadForm(FlaskForm):
    """
    Form for users to add new energy bill
    """
    # TODO add more fields
    file = FileField()
    name = StringField('Name', validators=[DataRequired()])
    physical_quantity = SelectField('Physical quantity', validators=[DataRequired()],
                                    choices=[("emission", "Emission"), ("concentration", "concentration")])
    year = SelectField('Year', validators=[DataRequired()],
                       choices=[(year, year) for year in range(1900, 2101)])
    submit = SubmitField('Submit')
