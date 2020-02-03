"common & util"

from __future__ import annotations # for classmethod return type
import contextlib, os, socket
from dataclasses import dataclass
import flask, psycopg2.pool, werkzeug

POOL = None

def init_pool(_setup_state):
  global POOL
  if POOL is None:
    POOL = psycopg2.pool.ThreadedConnectionPool(0, 4, os.environ['AUTOMIG_CON'])

@contextlib.contextmanager
def withcon():
  "helper to get / return a DB pool connection"
  # todo: move to util
  con = POOL.getconn()
  try: yield con
  finally:
    POOL.putconn(con)

def strip_empty(form):
  "return copy of form with empty fields removed"
  return {key: val for key, val in form.items() if val}

def insert_stmt(table, returning, db_fields):
  "helper to generate an insert stmt from db_fields dict"
  keys = ', '.join(db_fields)
  subs = ', '.join(f"%({key})s" for key in db_fields)
  stmt = f"insert into {table} ({keys}) values ({subs})"
  if returning:
    stmt += f" returning {returning}"
  return stmt

@dataclass
class Bracket:
  "rounding helper"
  lower: int
  upper: int

  def __lt__(self, other):
    return (self.lower, self.upper) < (other.lower, other.upper)

  def __hash__(self):
    return hash((self.lower, self.upper))

  @classmethod
  def round(cls, count: int) -> Bracket:
    "round a count to a bracket"
    if count < 1:
      raise ValueError("round() takes values >= 1, you passed", count)
    bucket = 10 if count < 100 else 100
    bottom = count - (count % bucket)
    return cls(bottom or 1, bottom + bucket - 1)

  def render(self):
    return f"{self.lower} - {self.upper}"

def host_is_ip(forwarded_host):
  "or localhost"
  sans_port = forwarded_host.split(':')[0]
  if sans_port == 'localhost':
    return True
  try:
    socket.inet_aton(sans_port)
    return True
  except socket.error:
    return False

# pylint: disable=inconsistent-return-statements
def ssl_middleware():
  """Janky HSTS that doesn't engage when host is an IP address, i.e. health checks.
  Using this instead of flask-talisman because GKE ingress has wrong health check path.
  https://cloud.google.com/kubernetes-engine/docs/concepts/ingress#health_checks
  """
  req = flask.request
  if not host_is_ip(werkzeug.wsgi.get_host(req.environ)) and not (req.is_secure or req.headers.get('X-Forwarded-Proto') == 'https'):
    return flask.redirect(req.url.replace('http://', 'https://', 1))
