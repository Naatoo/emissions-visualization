from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, StringField, SelectField
from wtforms.validators import DataRequired


class UploadFileForm(FlaskForm):
    """
    Form for uploading a new file
    """
    file = FileField(validators=[DataRequired()])
    submit = SubmitField('Upload')
