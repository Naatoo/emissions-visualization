from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, StringField, SelectField
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
    year = SelectField('Year', validators=[DataRequired()],
                       choices=[(year, year) for year in range(1900, 2101)], default=2015)
    submit = SubmitField('Submit')
