from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.fields.html5 import DecimalField
from wtforms.validators import DataRequired

from app.tools.paths import COUNTRIES_TXT_FILE


def load_countries():
    with open(COUNTRIES_TXT_FILE) as file:
        for line in file.readlines():
            yield line.strip().split(",")


class MapForm(FlaskForm):
    """
    Form for users to add new energy bill
    """

    zoom = SelectField('Zoom', validators=[DataRequired()],
                       choices=[("1", "No zooming"), ("2", "x2"), ("3", "x3"),
                                ("5", "x5"), ("10", "x10"), ("25", "x25")], default=2)
    interpolation_type = SelectField("Interpolation type", validators=[DataRequired()],
                                     choices=[(0, "Nearest neighbour"), (1, "Bilinear"), (3, "Bicubic")], default=3)
    line_opacity = SelectField('Line opacity', validators=[DataRequired()],
                            choices=[((round(val * 0.1, 1)), round((val * 0.1), 1)) for val in range(11)])
    fill_opacity = SelectField('Fill opacity', validators=[DataRequired()],
                            choices=[((round(val * 0.1, 1)), round((val * 0.1), 1)) for val in range(11)], default=0.7)
    color = SelectField('Colors', choices=[(color, color) for color in [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']], default="Oranges")
    submit = SubmitField('Refresh')
    # TODO: validators


class LatLonForm(MapForm):
    lon_max = DecimalField('Longitude End', validators=[DataRequired()], default=20)
    lon_min = DecimalField('Longitude Start', validators=[DataRequired()], default=10)
    lat_min = DecimalField('Latitude Start', validators=[DataRequired()], default=40.9)
    lat_max = DecimalField('Latitude End', validators=[DataRequired()], default=50.9)


class CountryForm(MapForm):
    country = SelectField('Country', choices=[(code, country) for (country, code) in load_countries()])
