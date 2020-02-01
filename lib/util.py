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
