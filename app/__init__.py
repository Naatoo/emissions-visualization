from flask import Flask, render_template, send_file, redirect, url_for

from flask_bootstrap import Bootstrap
from numpy import mean
import os
from .home import home as home_blueprint
from app.home.views import generate_map


def create_app():
    generate_map()
    app = Flask(__name__)
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    Bootstrap(app)
    app.register_blueprint(home_blueprint)

    return app

