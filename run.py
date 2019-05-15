from flask import Flask, render_template, send_file, redirect, url_for

from csv_parser import CSVFileParser
from interpolator import Interpolator
from interactive_map import InteractiveMap
from map_zoom_form import MapForm
from flask_bootstrap import Bootstrap
from numpy import mean
import os


def create_csv_json_files(boundaries: dict, zoom_value: int) -> None:
    order = 5
    source_file_name = "PM10_raw.txt"
    target_file_name = "PM10_zoomed"
    country_code = "PL"
    parser = CSVFileParser(source_file_name, **{"country": country_code})
    interpolator = Interpolator(target_file_name, parser.data, parser.coordinates, boundary_values=boundaries)
    interpolator.interpolate(zoom_value=zoom_value, order=order)


def generate_map(form=None):
    global m
    if not form:
        boundaries = {
            "lat_min": 19.55,
            "lat_max": 20.55,
            "lon_min": 49.55,
            "lon_max": 50.05
        }
        create_csv_json_files(boundaries=boundaries,
                              zoom_value=2)

        m = InteractiveMap(fill_color="Oranges",
                           fill_opacity=0.5,
                           line_opacity=0.3,
                           default_location=(50, 20),
                           default_zoom=8).map
    else:
        boundaries = {
            "lat_min": form.lat_min.data,
            "lat_max": form.lat_max.data,
            "lon_min": form.lon_min.data,
            "lon_max": form.lon_max.data
        }
        create_csv_json_files(boundaries=boundaries,
                              zoom_value=int(form.interpolation.data))

        default_lat = mean([boundaries["lat_min"], boundaries["lat_max"]]) / 1000
        default_lon = mean([boundaries["lon_min"], boundaries["lon_max"]]) / 1000
        # global m
        print(default_lat)
        m = InteractiveMap(fill_color=form.color.data,
                           fill_opacity=form.fill_opacity.data,
                           line_opacity=form.line_opacity.data,
                           default_location=(default_lon, default_lat)).map


generate_map()
app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
bootstrap = Bootstrap(app)


@app.route('/map_render')
def map_render():
    return m.get_root().render()


@app.route('/map_final', methods=['GET', 'POST'])
def map_final():
    form = MapForm()
    if form.is_submitted():
        generate_map(form)
        return redirect(url_for("map_final"))
    return render_template("map_final.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)