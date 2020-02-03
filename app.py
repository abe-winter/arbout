"app.py -- flask entry-point"

import flask
from lib import core_blueprint
from lib.util import SSLMiddleware

APP = flask.Flask(__name__)
APP.wsgi_app = SSLMiddleware(APP.wsgi_app)
APP.register_blueprint(core_blueprint.CORE)
