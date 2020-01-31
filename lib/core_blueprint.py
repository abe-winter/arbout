"core_blueprint.py -- flask Blueprint for core functionality"

import json, os, re
from dataclasses import dataclass
import flask
from marshmallow import Schema, fields, validate, validates, ValidationError

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
  CatPair('npay', 'Underpaid or paid late'),
  CatPair('other', 'Other'),
]

AFFIRMATION = """I affirm, on penalty of perjury, that I believe my submission to be (1) accurate and (2) not a duplicate submission.

I understand that submitting information to this database could expose me to legal risks."""

@CORE.route('/submit')
def get_submit():
  return flask.render_template('submit.jinja.htm', categories=CATEGORIES, affirmation=AFFIRMATION, states=STATES)

YESNO = fields.Str(validate=validate.OneOf(['yes', 'no']), required=True)

def month(required=False):
  return fields.Str(validate=validate.Regexp(r'\d{4}-\d{2}'))

class SubmissionSchema(Schema):
  claimant = YESNO
  issue_cat = fields.Str(validate=validate.OneOf([cat.key for cat in CATEGORIES]), required=True)
  issue_det = fields.Str()
  terms_link = fields.URL()
  you_negotiate = YESNO
  sought_dollars = fields.Int()
  settlement_dollars = fields.Int()
  favor = YESNO
  fair = YESNO
  incident_date = month()
  dispute_date = month()
  file_date = month()
  arb_date = month(True)
  agency = fields.Str()
  state = fields.Str(validate=validate.OneOf([row[0] for row in STATES]), required=True)
  chose = fields.Str(validate=validate.OneOf(['yes', 'yes_list', 'no']), required=True)
  case_real_id = fields.Str()
  email = fields.Email()
  password = fields.Str()
  affirm = fields.Str(required=True)

  def valid_affirm(self, value):
    if value.replace('\r\n', '\n') != AFFIRMATION:
      raise ValidationError('invalid affirmation')

def strip_empty(form):
  "return copy of form with empty fields removed"
  return {key: val for key, val in form.items() if val}

@CORE.route('/submit', methods=['POST'])
def post_submit():
  errors = SubmissionSchema().validate(strip_empty(flask.request.form))
  if errors:
    return flask.Response(
      json.dumps({"message": "Bad form input. Contact support if this seems to be a bug", "errors": errors}, indent=2),
      status=400,
      mimetype="application/json"
    )
  raise NotImplementedError

@CORE.route('/search')
def get_search():
  raise NotImplementedError

@CORE.route('/search', methods=['POST'])
def post_search():
  raise NotImplementedError
