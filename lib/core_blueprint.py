"core_blueprint.py -- flask Blueprint for core functionality"

import flask

CORE = flask.Blueprint('core', __name__)

@CORE.route('/')
def splash():
  return flask.render_template('splash.jinja.htm')

@CORE.route('/submit')
def get_submit():
  raise NotImplementedError

@CORE.route('/submit', methods=['POST'])
def post_submit():
  raise NotImplementedError

@CORE.route('/search')
def get_search():
  raise NotImplementedError

@CORE.route('/search', methods=['POST'])
def post_search():
  raise NotImplementedError
