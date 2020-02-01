import pytest
from lib import diff_summary, search
from lib.diff_summary import Bracket

def test_round():
  pairs = [
    (diff_summary.round(1), Bracket(lower=1, upper=9)),
    (diff_summary.round(5), Bracket(lower=1, upper=9)),
    (diff_summary.round(10), Bracket(lower=10, upper=19)),
    (diff_summary.round(11), Bracket(lower=10, upper=19)),
    (diff_summary.round(19), Bracket(lower=10, upper=19)),
    (diff_summary.round(20), Bracket(lower=20, upper=29)),
    (diff_summary.round(50), Bracket(lower=50, upper=59)),
    (diff_summary.round(99), Bracket(lower=90, upper=99)),
    (diff_summary.round(100), Bracket(lower=100, upper=199)),
    (diff_summary.round(101), Bracket(lower=100, upper=199)),
    (diff_summary.round(500), Bracket(lower=500, upper=599)),
    (diff_summary.round(550), Bracket(lower=500, upper=599)),
    (diff_summary.round(1000), Bracket(lower=1000, upper=1099)),
    (diff_summary.round(1001), Bracket(lower=1000, upper=1099)),
    (diff_summary.round(1200), Bracket(lower=1200, upper=1299)),
  ]
  actual, expected = zip(*pairs)
  assert actual == expected
  with pytest.raises(ValueError):
    diff_summary.round(0)

def test_diff_group_counterparty(monkeypatch):
  monkeypatch.setattr(search, 'GROUP_THRESHOLD', 2)
  rows = [
    diff_summary.CaseRow(counterparty='hey'),
    diff_summary.CaseRow(counterparty_domain='hey.com'),
    diff_summary.CaseRow(counterparty='hey', counterparty_domain='hey.com'),
    diff_summary.CaseRow(counterparty='3'),
  ]
  assert {k: len(v) for k, v in diff_summary.diff_group_counterparty(rows).items()} == \
    {('domain', 'hey.com'): 2}

def test_diff_summarize_counterparty():
  raise NotImplementedError
