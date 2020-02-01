"search.py -- convert searches to queries"

from datetime import date
from dataclasses import dataclass
from typing import Optional

GROUP_THRESHOLD = 10
PCT_THRESHOLD = 0.1 # i.e. 10%

class Search:
  "constraints for a search"
  counterparty: Optional[str]
  counterparty_domain: Optional[str]
  start_date: Optional[date]
  end_date: Optional[date]
  sought_dollars: Optional[int]
  settlement_dollars: Optional[int]
  issue_category: Optional[str]

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
