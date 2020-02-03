"core_blueprint.py -- flask Blueprint for core functionality"

import binascii, json, os
from dataclasses import dataclass
import flask, scrypt
from marshmallow import Schema, fields, validate, ValidationError
from .util import init_pool, insert_stmt, strip_empty, withcon
from . import diff_summary, search

CORE = flask.Blueprint('core', __name__)
STATES = json.load(open(os.path.join(os.path.split(__file__)[0], 'states.json')))['states']
GLOBAL_SALT = binascii.unhexlify(os.environ['ARB_SALT'])
CRYPT = binascii.unhexlify(os.environ['ARB_CRYPT'])

@CORE.context_processor
def inject_version():
  return {'version': os.environ.get('VERSION')}

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
CAT_LOOKUP = {pair.key: pair.label for pair in CATEGORIES}

AFFIRMATION = """I affirm, on penalty of perjury, that I believe my submission to be (1) accurate and (2) not a duplicate submission.

I understand that submitting information to this database could expose me to legal risks."""

@CORE.route('/submit')
def get_submit():
  return flask.render_template('submit.jinja.htm', categories=CATEGORIES, affirmation=AFFIRMATION, states=STATES)

def yesno(required=False):
  return fields.Str(validate=validate.OneOf(['yes', 'no']), required=required)

class SubmissionSchema(Schema):
  counterparty = fields.Str()
  counterparty_domain = fields.Str()
  claimant = yesno(True)
  issue_cat = fields.Str(validate=validate.OneOf([cat.key for cat in CATEGORIES]), required=True)
  issue_det = fields.Str()
  terms_link = fields.Str()
  you_negotiate = yesno()
  sought_dollars = fields.Int()
  settlement_dollars = fields.Int()
  favor = yesno()
  fair = yesno()
  incident_date = fields.DateTime(format='%Y-%m')
  dispute_date = fields.DateTime(format='%Y-%m')
  file_date = fields.DateTime(format='%Y-%m')
  arb_date = fields.DateTime(format='%Y-%m', required=True)
  agency = fields.Str()
  state = fields.Str(validate=validate.OneOf([row[0] for row in STATES]), required=True)
  chose = fields.Str(validate=validate.OneOf(['yes', 'yes_list', 'no']))
  case_real_id = fields.Str()
  email = fields.Email()
  password = fields.Str()
  affirm = fields.Str(required=True)

  @staticmethod
  def valid_affirm(value):
    if value.replace('\r\n', '\n') != AFFIRMATION:
      raise ValidationError('invalid affirmation')

@CORE.errorhandler(ValidationError)
def handle_validation_error(err):
  return flask.render_template('invalid.jinja.htm', messages=err.messages)

def yesno_null(value):
  "cast non-null yesno to bool"
  # todo: do this with marshmallow
  return {'yes': True, 'no': False, None: None}[value]

def date_null(value):
  return value and value.date()

@CORE.route('/submit', methods=['POST'])
def post_submit():
  # ValidationError here gets caught by middleware
  parsed = SubmissionSchema().load(strip_empty(flask.request.form))
  db_fields = {
    'counterparty': parsed.get('counterparty'),
    'counterparty_domain': parsed.get('counterparty_domain'),
    'submitter_initiated': yesno_null(parsed.get('claimant')),
    'issue_category': parsed.get('issue_cat'),
    'issue': parsed.get('issue_det'),
    'terms_link': parsed.get('terms_link'),
    'draft_contract': yesno_null(parsed.get('you_negotiate')),
    'sought_dollars': parsed.get('sought_dollars'),
    'settlement_dollars': parsed.get('settlement_dollars'),
    'subjective_inmyfavor': yesno_null(parsed.get('favor')),
    'subjective_fair': yesno_null(parsed.get('fair')),
    'incident_date': date_null(parsed.get('incident_date')),
    'dispute_date': date_null(parsed.get('dispute_date')),
    'file_date': date_null(parsed.get('file_date')),
    'arbitration_date': date_null(parsed.get('arb_date')),
    'arbitration_agency': parsed.get('agency'),
    # todo: agency domain
    'arbitration_state': parsed.get('state'),
    'submitter_choose_agency': parsed.get('chose'),
    'affirm': parsed.get('affirm'),
  }
  if 'email' in parsed:
    # todo: hash is wrong here. it's for dispute handling and nothing else -- we need to be able to decrypt it
    db_fields['email_hash'] = scrypt.hash(parsed['email'], GLOBAL_SALT)
  if 'case_real_id' in parsed:
    db_fields['real_id_hash'] = scrypt.hash(parsed['case_real_id'], GLOBAL_SALT)
  if 'password' in parsed:
    salt = os.urandom(12)
    db_fields['password_salt'] = salt
    db_fields['password_hash'] = scrypt.hash(parsed['password'], salt)
  with withcon() as con, con.cursor() as cur:
    cur.execute(insert_stmt('cases', 'caseid', db_fields), db_fields)
    con.commit()
  return flask.render_template('after_submit.jinja.htm')

@CORE.route('/search')
def get_search():
  return flask.render_template('search.jinja.htm', categories=CATEGORIES, states=STATES)

@CORE.route('/search', methods=['POST'])
def post_search():
  # todo: look into marshmallow-dataclass so we're not relying on psycopg2 / libpq for sanitization
  rows = search.search(search.Search(**strip_empty(flask.request.form)))
  groups = diff_summary.diff_group_counterparty(rows)
  summaries = [diff_summary.summarize(key, rows) for key, rows in groups.items()]
  # note: sorting by party key so stable sort doesn't reveal relative sizes
  summaries.sort(key=lambda summary: (summary.total, summary.key))
  # todo: paging
  summaries = summaries[:20]
  for summary in summaries:
    for approx in summary.issue_cats:
      approx.label = CAT_LOOKUP.get(approx.label, approx.label)
    for approx in summary.settlement_dollars:
      approx.label = f"${approx.label.lower} - ${approx.label.upper}"
  return flask.render_template('serp.jinja.htm', summaries=summaries)

@CORE.route('/disputes')
def disputes():
  return flask.render_template('dispute.jinja.htm')

@CORE.route('/terms')
def terms():
  return flask.render_template('terms.jinja.htm')
