"diff_summary.py -- differential-aware search results summarization"

import itertools
from dataclasses import dataclass
from typing import List
from . import search
from .search import CaseRow

def counterparty_key(row: CaseRow):
  return ('domain', row.counterparty_domain) if row.counterparty_domain else ('name', row.counterparty)

def diff_group_counterparty(rows: List[CaseRow]):
  """Grouping key is (counterparty_domain or counterparty).
  Respects global GROUP_THRESHOLD by stripping smaller groups.
  """
  sorted_ = sorted(rows, key=counterparty_key)
  ret = {
    key: list(inner_rows)
    for key, inner_rows in itertools.groupby(sorted_, key=counterparty_key)
  }
  too_small = []
  for key, val in ret.items():
    if len(val) < search.GROUP_THRESHOLD:
      too_small.append(key)
  for key in too_small:
    del ret[key]
  return ret

@dataclass
class Bracket:
  lower: int
  upper: int

def round_bucket(count) -> [int, int]:
  "round a count to a bracket"
  if count < 1:
    raise ValueError("round() takes values >= 1, you passed", count)
  bucket = 10 if count < 100 else 100
  bottom = count - (count % bucket)
  return Bracket(bottom or 1, bottom + bucket - 1)

class ApproxLabel:
  rounded_count: int
  label: str

class ApproxRange:
  rounded_count: int
  other: bool # if true, bottom & top are ignored. is there an 'either' type?
  bottom: float
  top: float

class Summary:
  counterparty_key_type: str
  counterparty: str
  agencies: List[ApproxLabel]
  issue_cats: List[ApproxLabel]
  issues: List[ApproxLabel]
  incident_years: List[ApproxLabel]
  dispute_years: List[ApproxLabel]
  arbitration_years: List[ApproxLabel]
  sought_dollars: List[ApproxRange]
  settle_over_sought: List[ApproxRange]
  fair: List[ApproxLabel]
  in_my_favor: List[ApproxLabel]
  removed: List[ApproxLabel] # 'yes' means records were removed after a correctness or other dispute
  chose_agency: List[ApproxLabel]
  states: List[ApproxLabel]

def diff_summarize_counterparty(rows) -> Summary:
  "operates on each dict value of diff_group_counterparty ret"
  raise NotImplementedError
