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
    line_opacity = SelectField('Line opacity', validators=[DataRequired()],
                               choices=[((round(val * 0.1, 1)), round((val * 0.1), 1)) for val in range(11)])
    fill_opacity = SelectField('Fill opacity', validators=[DataRequired()],
                               choices=[((round(val * 0.1, 1)), round((val * 0.1), 1)) for val in range(11)],
                               default=0.7)
    color = SelectField('Colors', choices=[('Greys', 'Greys'), ('Purples', 'Purples'), ('Blues', 'Blues'),
                                           ('Greens', 'Greens'), ('Oranges', 'Oranges'), ('Reds', 'Reds'),
                                           ('YlOrBr', "YellowOrangeBrown "), ('YlOrRd', 'YellowOrangeRed'),
                                           ('OrRd', "OrangeRed"), ('PuRd', 'PurpleRed'), ('RdPu', 'RedPurple'),
                                           ('BuPu', "BluePurple"), ('GnBu', "GreenBlue"), ('PuBu', "PurpleBlue"),
                                           ('YlGnBu', "YellowGreenBlue"), ('PuBuGn', "PurpleBlueGreen"),
                                           ('BuGn', "BlueGreen"), ('YlGn', "YellowGreen")], default="Oranges")
    submit = SubmitField('Refresh')


class InterpolationForm(MapForm):
    zoom = SelectField('Zoom', validators=[DataRequired()],
                       choices=[("1", "No zooming"), ("2", "x2"), ("3", "x3"), ("5", "x5"), ("10", "x10")], default=1)
    interpolation_type = SelectField("Interpolation type", validators=[DataRequired()],
                                     choices=[(0, "Nearest neighbour"), (1, "Bilinear"), (3, "Bicubic")], default=3)


class LatLonForm(InterpolationForm):
    lon_min = DecimalField('Longitude Start', validators=[DataRequired()])
    lon_max = DecimalField('Longitude End', validators=[DataRequired()])
    lat_min = DecimalField('Latitude Start', validators=[DataRequired()])
    lat_max = DecimalField('Latitude End', validators=[DataRequired()])


class CountryForm(InterpolationForm):
    country = SelectField('Country', choices=[(code, country) for (country, code) in load_countries()], default="PL")
