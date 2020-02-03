"search.py -- convert searches to queries"

from datetime import date
from dataclasses import dataclass, fields
from typing import List, Optional
import psycopg2.extras
from .util import Bracket, withcon

class WhereClause:
  "builder for whereclause"

  def __init__(self):
    self.terms = []
    self.params = {}

  def add(self, sql_name, value, operator='=', transform=None, ignore_null=True): # pylint: disable=too-many-arguments
    "transform is when you want to use a column expression that won't work with %()s"
    if value is None:
      if ignore_null:
        return
      else:
        raise NotImplementedError("todo 'is null'")
    self.terms.append(f'{transform or sql_name} {operator} %({sql_name})s')
    self.params[sql_name] = value

  def clause(self):
    return ' and '.join(self.terms)

@dataclass
class Search:
  "constraints for a search"
  party: Optional[str] = None
  party_domain: Optional[str] = None
  start_year: Optional[int] = None
  end_year: Optional[int] = None
  min_settlement_dollars: Optional[int] = None
  issue_category: Optional[str] = None
  state: Optional[str] = None

  def empty(self):
    return all(getattr(self, field.name, None) is None for field in fields(Search))

  def whereclause(self):
    "render the search to a sql query"
    where = WhereClause()
    where.add('counterparty', self.party)
    where.add('counterparty_domain', self.party_domain)
    where.add('start_year', self.start_year, operator='>=', transform='extract(year from arbitration_date)')
    where.add('end_year', self.end_year, operator='<=', transform='extract(year from arbitration_date)')
    if self.min_settlement_dollars:
      where.add('settlement_dollars', Bracket.round(self.min_settlement_dollars).lower, operator='>=')
    where.add('issue_category', self.issue_category)
    where.add('arbitration_state', self.state)
    return where

@dataclass
class CaseRow:
  "representation of database row"
  counterparty: str
  counterparty_domain: Optional[str] = None
  issue_category: Optional[str] = None
  incident_date: Optional[date] = None
  dispute_date: Optional[date] = None
  file_date: Optional[date] = None
  arbitration_date: Optional[date] = None
  sought_dollars: Optional[int] = None
  settlement_dollars: Optional[int] = None
  subjective_fair: Optional[bool] = None
  subjective_inmyfavor: Optional[bool] = None
  submitter_initiated: Optional[bool] = None
  arbitration_agency: Optional[str] = None
  submitter_choose_agency: Optional[str] = None
  arbitration_state: Optional[str] = None
  draft_contract: Optional[bool] = None
  terms_link: Optional[str] = None
  removed: bool = False

def search(terms: Search) -> List[CaseRow]:
  if terms.empty():
    raise ValueError("empty search")
  where = terms.whereclause()
  names = [field.name for field in fields(CaseRow)]
  query = f"select {', '.join(names)} from cases where {where.clause()}"
  with withcon() as con, con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
    cur.execute(query, where.params)
    return [CaseRow(**row) for row in cur.fetchall()]
