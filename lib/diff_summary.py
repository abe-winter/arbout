"diff_summary.py -- differential-aware search results summarization"

def counterparty_key(row):
  return ('domain', row.counterparty_domain) if row.counterparty_domain else ('name', row.counterparty)

def diff_group_counterparty(rows):
  """Grouping key is (counterparty_domain or counterparty).
  Respects global THRESHOLDs.
  """
  sorted_ = sorted(rows, key=counterparty_key)
  return dict(itertools.groupby(sorted_, key=counterparty_key))

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
  agencies: ApproxLabel[]
  issue_cats: ApproxLabel[]
  issues: ApproxLabel[]
  incident_years: ApproxLabel[]
  dispute_years: ApproxLabel[]
  arbitration_years: ApproxLabel[]
  sought_dollars: ApproxRange[]
  settle_over_sought: ApproxRange[]
  fair: ApproxLabel[]
  in_my_favor: ApproxLabel[]
  removed: ApproxLabel[] # removed after a dispute
  chose_agency: ApproxLabel[]
  states: ApproxLabel[]

def diff_summarize_counterparty(rows) -> Summary[]:
  "operates on each dict value of diff_group_counterparty ret"
  raise NotImplementedError
