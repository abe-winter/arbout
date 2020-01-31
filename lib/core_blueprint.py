"core_blueprint.py -- flask Blueprint for core functionality"

import base64, contextlib, json, os, re
from dataclasses import dataclass
from datetime import date
import flask, psycopg2.pool
from marshmallow import Schema, fields, validate, validates, ValidationError

CORE = flask.Blueprint('core', __name__)
STATES = json.load(open(os.path.join(os.path.split(__file__)[0], 'states.json')))['states']
POOL = None
GLOBAL_SALT = base64.b64decode(os.environ['ARB_SALT'])

def init_pool(setup_state):
  global POOL
  if POOL is None:
    POOL = psycopg2.pool.ThreadedConnectionPool(0, 4, os.environ['AUTOMIG_CON'])

# todo: would rather this happened at app startup vs registration i.e. import.
# But before_first_request is too late.
CORE.record(init_pool)

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

def yesno(required=False):
  return fields.Str(validate=validate.OneOf(['yes', 'no']), required=required)

def month(required=False):
  return fields.Str(validate=validate.Regexp(r'\d{4}-\d{2}'), required=required)

class SubmissionSchema(Schema):
  counterparty = fields.Str()
  counterparty_domain = fields.URL()
  claimant = yesno(True)
  issue_cat = fields.Str(validate=validate.OneOf([cat.key for cat in CATEGORIES]), required=True)
  issue_det = fields.Str()
  terms_link = fields.URL()
  you_negotiate = yesno()
  sought_dollars = fields.Int()
  settlement_dollars = fields.Int()
  favor = yesno()
  fair = yesno()
  incident_date = month()
  dispute_date = month()
  file_date = month()
  arb_date = month(True)
  agency = fields.Str()
  state = fields.Str(validate=validate.OneOf([row[0] for row in STATES]), required=True)
  chose = fields.Str(validate=validate.OneOf(['yes', 'yes_list', 'no']))
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

@contextlib.contextmanager
def withcon():
  "helper to get / return a DB pool connection"
  # todo: move to util
  con = POOL.getconn()
  try: yield con
  finally:
    POOL.putconn(con)

def insert_stmt(table, returning, fields):
  "helper to generate an insert stmt from fields dict"
  # todo: move to util
  keys = ', '.join(fields)
  subs = ', '.join(f"%({key})s" for key in fields)
  stmt = f"insert into {table} ({keys}) values ({subs})"
  if returning:
    stmt += f" returning {returning}"
  return stmt

@CORE.errorhandler(ValidationError)
def handle_validation_error(err):
  return flask.render_template('invalid.jinja.htm', messages=err.messages)

def parse_month(raw):
  # todo: do this in marshmallow
  if raw is None:
    return raw
  return date(int(raw[:4]), int(raw[5:7]), 1)

@CORE.route('/submit', methods=['POST'])
def post_submit():
  # ValidationError here gets caught by middleware
  parsed = SubmissionSchema().load(strip_empty(flask.request.form))
  db_fields = {
    'counterparty': parsed.get('counterparty'),
    'counterparty_domain': parsed.get('counterparty_domain'),
    'submitter_initiated': parsed.get('claimant'),
    'issue_category': parsed.get('issue_cat'),
    'issue': parsed.get('issue_det'),
    'terms_link': parsed.get('terms_link'),
    'draft_contract': parsed.get('you_negotiate'),
    'sought_dollars': parsed.get('sought_dollars'),
    'settlement_dollars': parsed.get('settlement_dollars'),
    'subjective_inmyfavor': parsed.get('favor'),
    'subjective_fair': parsed.get('fair'),
    'incident_date': parse_month(parsed.get('incident_date')),
    'dispute_date': parse_month(parsed.get('dispute_date')),
    'file_date': parse_month(parsed.get('file_date')),
    'arbitration_date': parse_month(parsed.get('arb_date')),
    'arbitration_agency': parsed.get('agency'),
    # todo: agency domain
    'arbitration_state': parsed.get('state'),
    'submitter_choose_agency': parsed.get('chose'),
    'affirm': parsed.get('affirm'),
  }
  # '': parsed.get('email'), # and salt # email_hash
  # '': parsed.get('case_real_id'), # and salt # real_id_hash
  # '': parsed.get('password'), # with custom salt
  # password_salt
  # password_hash
  with withcon() as con, con.cursor() as cur:
    cur.execute(insert_stmt('cases', 'caseid', db_fields), db_fields)
    con.commit()
  return flask.render_template('after_submit.jinja.htm')

@CORE.route('/search')
def get_search():
  raise NotImplementedError

@CORE.route('/search', methods=['POST'])
def post_search():
  raise NotImplementedError
