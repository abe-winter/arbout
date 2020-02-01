"diff_summary.py -- differential-aware search results summarization"

from __future__ import annotations # for classmethod return type
import collections, itertools
from dataclasses import dataclass
from typing import List, Dict, Generator, Optional, Union
from . import search
from .search import CaseRow

@dataclass
class CounterpartyLabel:
  "groupable domain / name"
  kind: str
  value: str

  def __lt__(self, other):
    return (self.kind, self.value) < (other.kind, other.value)

  def __hash__(self):
    return hash((self.kind, self.value))

  @classmethod
  def key(cls, row: CaseRow) -> CounterpartyLabel:
    return cls('domain', row.counterparty_domain) if row.counterparty_domain else cls('name', row.counterparty)

def diff_group_counterparty(rows: List[CaseRow]) -> Dict[CounterpartyLabel, List[CaseRow]]:
  """Grouping key is (counterparty_domain or counterparty).
  Respects global GROUP_THRESHOLD by stripping smaller groups.
  """
  sorted_ = sorted(rows, key=CounterpartyLabel.key)
  ret = {
    key: list(inner_rows)
    for key, inner_rows in itertools.groupby(sorted_, key=CounterpartyLabel.key)
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

@dataclass
class ApproxLabel:
  label: Union[str, int, Bracket]
  bracket: Bracket

  @classmethod
  def make(cls, values: Union[List, Generator]) -> List[ApproxLabel]:
    "summarize attr from rows according to group_threshold"
    ret = [
      cls(value, Bracket.round(count))
      # note: sorted() below instead of most_common() so we don't leak non-rounded counts
      for value, count in sorted(collections.Counter(value for value in values if value is not None).items())
      if count >= search.GROUP_THRESHOLD
    ]
    return sorted(ret, reverse=True, key=lambda approx: approx.bracket)

@dataclass
class Summary:
  total: Bracket
  removed: Optional[Bracket] # 'yes' means records were removed after a correctness or other dispute
  agencies: List[ApproxLabel]
  issue_cats: List[ApproxLabel]
  arbitration_years: List[ApproxLabel]
  settlement_dollars: List[ApproxLabel]
  fair: List[ApproxLabel]
  drafted: List[ApproxLabel]
  chose_agency: List[ApproxLabel]
  states: List[ApproxLabel]

def summarize(rows: List[CaseRow]) -> Summary:
  "rolls up a list of cases, giving more details when the threshold is met"
  removed = sum(row.removed for row in rows)
  return Summary(
    total=Bracket.round(len(rows)),
    removed=Bracket.round(removed) if removed else None,
    agencies=ApproxLabel.make(row.arbitration_agency for row in rows),
    issue_cats=ApproxLabel.make(row.issue_category for row in rows),
    arbitration_years=ApproxLabel.make(row.arbitration_date.year for row in rows if row.arbitration_date),
    settlement_dollars=ApproxLabel.make(Bracket.round(row.settlement_dollars) for row in rows if row.settlement_dollars is not None),
    fair=ApproxLabel.make(row.subjective_fair for row in rows),
    chose_agency=ApproxLabel.make(row.submitter_choose_agency for row in rows),
    drafted=ApproxLabel.make(row.draft_contract for row in rows),
    states=ApproxLabel.make(row.arbitration_state for row in rows),
  )
