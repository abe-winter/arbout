"search.py -- convert searches to queries"

import itertools
from typing import Optional
from datetime import date

GROUP_THRESHOLD = 10
REPORT_THRESHOLD = 20
PCT_THRESHOLD = 0.25 # i.e. 25%

class Search:
  counterparty: Optional[str]
  counterparty_domain: Optional[str]
  start_date: Optional[date]
  end_date: Optional[date]
  sought_dollars: Optional[int]
  settlement_dollars: Optional[int]
  issue_category: Optional[str]
