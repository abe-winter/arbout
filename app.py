"app.py -- flask entry-point"

import flask
from lib import core_blueprint
from lib.util import ssl_middleware

APP = flask.Flask(__name__)
APP.before_request(ssl_middleware)
APP.register_blueprint(core_blueprint.CORE)
