"core_blueprint.py -- flask Blueprint for core functionality"

import json, os
from dataclasses import dataclass
import flask

CORE = flask.Blueprint('core', __name__)
STATES = json.load(open(os.path.join(os.path.split(__file__)[0], 'states.json')))['states']

@CORE.route('/')
def splash():
  return flask.render_template('splash.jinja.htm')

@dataclass
class CatPair:
  key: str
  label: str

CATEGORIES = [
  CatPair('nadvert', 'Not as advertised'),
  CatPair('ndeliv', 'Never delivered'),
  CatPair('nwork', "Doesn't work"),
  CatPair('price', "Overcharged, undercharged, or bad price"),
  CatPair('navail', 'Outage or intermittent availability'),
  CatPair('ncompat', 'Not compatible with other stuff'),
  CatPair('mistreat', 'Mistreatment by company'),
  CatPair('woreout', 'Wore out quickly'),
  CatPair('danger', 'Dangerous or caused an injury'),
  CatPair('late', 'Arrived late'),
  CatPair('other', 'Other'),
]

AFFIRMATION = """I affirm, on penalty of perjury, that I believe my submission to be (1) accurate and (2) not a duplicate submission.

I understand that submitting information to this database could expose me to legal risks."""

@CORE.route('/submit')
def get_submit():
  return flask.render_template('submit.jinja.htm', categories=CATEGORIES, affirmation=AFFIRMATION, states=STATES)

@CORE.route('/submit', methods=['POST'])
def post_submit():
  raise NotImplementedError

@CORE.route('/search')
def get_search():
  raise NotImplementedError

@CORE.route('/search', methods=['POST'])
def post_search():
  raise NotImplementedError
