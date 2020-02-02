"common & util"

import contextlib, os
import psycopg2.pool

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
