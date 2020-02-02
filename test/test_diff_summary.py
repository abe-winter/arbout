from datetime import date
import pytest
from lib import diff_summary, search
from lib.diff_summary import ApproxLabel, Bracket, CounterpartyLabel

def test_round():
  pairs = [
    (Bracket.round(1), Bracket(lower=1, upper=9)),
    (Bracket.round(5), Bracket(lower=1, upper=9)),
    (Bracket.round(10), Bracket(lower=10, upper=19)),
    (Bracket.round(11), Bracket(lower=10, upper=19)),
    (Bracket.round(19), Bracket(lower=10, upper=19)),
    (Bracket.round(20), Bracket(lower=20, upper=29)),
    (Bracket.round(50), Bracket(lower=50, upper=59)),
    (Bracket.round(99), Bracket(lower=90, upper=99)),
    (Bracket.round(100), Bracket(lower=100, upper=199)),
    (Bracket.round(101), Bracket(lower=100, upper=199)),
    (Bracket.round(500), Bracket(lower=500, upper=599)),
    (Bracket.round(550), Bracket(lower=500, upper=599)),
    (Bracket.round(1000), Bracket(lower=1000, upper=1099)),
    (Bracket.round(1001), Bracket(lower=1000, upper=1099)),
    (Bracket.round(1200), Bracket(lower=1200, upper=1299)),
  ]
  actual, expected = zip(*pairs)
  assert actual == expected
  with pytest.raises(ValueError):
    Bracket.round(0)

def test_diff_group_counterparty(monkeypatch):
  monkeypatch.setattr(search, 'GROUP_THRESHOLD', 2)
  rows = [
    diff_summary.CaseRow(counterparty='hey'),
    diff_summary.CaseRow(counterparty='hey LLC', counterparty_domain='hey.com'),
    diff_summary.CaseRow(counterparty='hey', counterparty_domain='hey.com'),
    diff_summary.CaseRow(counterparty='other'),
  ]
  assert {k: len(v) for k, v in diff_summary.diff_group_counterparty(rows).items()} == \
    {CounterpartyLabel('domain', 'hey.com'): 2}

def test_ApproxLabel(monkeypatch):
  monkeypatch.setattr(search, 'GROUP_THRESHOLD', 2)
  assert ApproxLabel.make([1, 1, 2]) == [ApproxLabel(label=1, bracket=Bracket(lower=1, upper=9))]
  assert ApproxLabel.make(['a', 'a', 'a', 'b', 'b'] + ['c'] * 10 + ['d'] * 20) == [
    ApproxLabel(label='d', bracket=Bracket(lower=20, upper=29)),
    ApproxLabel(label='c', bracket=Bracket(lower=10, upper=19)),
    ApproxLabel(label='a', bracket=Bracket(lower=1, upper=9)),
    ApproxLabel(label='b', bracket=Bracket(lower=1, upper=9)),
  ]

def test_summarize(monkeypatch):
  monkeypatch.setattr(search, 'GROUP_THRESHOLD', 2)
  rows = [
    search.CaseRow(counterparty='', arbitration_agency='ABC', issue_category='what1', arbitration_date=date(2020, 1, 1), settlement_dollars=1000, subjective_fair=False, draft_contract=False, submitter_choose_agency=False, arbitration_state='NY'),
    search.CaseRow(counterparty='', arbitration_agency='ABC', issue_category='what2', arbitration_date=date(2020, 1, 1), settlement_dollars=1000, subjective_fair=None, draft_contract=False, submitter_choose_agency=False, arbitration_state='NY'),
    search.CaseRow(counterparty='', arbitration_agency='ABC', issue_category='what3', arbitration_date=date(2020, 1, 1), settlement_dollars=1000, subjective_fair=None, draft_contract=False, submitter_choose_agency=False, arbitration_state='NY'),
    search.CaseRow(counterparty='', arbitration_agency='ABD', issue_category='what4', arbitration_date=date(2020, 1, 1), settlement_dollars=1000, subjective_fair=None, draft_contract=False, submitter_choose_agency=False, arbitration_state='NY'),
    search.CaseRow(counterparty='', arbitration_agency='ABD', issue_category='what5', arbitration_date=date(2020, 1, 1), settlement_dollars=1000, subjective_fair=None, draft_contract=False, submitter_choose_agency=False, arbitration_state='NY'),
  ]
  key = CounterpartyLabel('', '')
  assert diff_summary.summarize(key, rows) == diff_summary.Summary(
    key=key,
    total=Bracket(lower=1, upper=9),
    removed=None,
    agencies=[ApproxLabel('ABC', Bracket(1, 9)), ApproxLabel('ABD', Bracket(1, 9))], # testing multiple values
    issue_cats=[], # testing small group rejection
    arbitration_years=[ApproxLabel(2020, Bracket(1, 9))],
    settlement_dollars=[ApproxLabel(Bracket(1000, 1099), Bracket(1, 9))],
    fair=[], # testing null rejection
    drafted=[ApproxLabel(False, Bracket(1, 9))],
    chose_agency=[ApproxLabel(False, Bracket(1, 9))],
    states=[ApproxLabel('NY', Bracket(1, 9))]
  )
