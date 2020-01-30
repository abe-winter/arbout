"app.py -- flask entry-point"

import flask
from lib import core_blueprint

APP = flask.Flask(__name__)
APP.register_blueprint(core_blueprint.CORE)
