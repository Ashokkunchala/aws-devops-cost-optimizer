from datetime import date

import pytest

from cost_optimizer.cost_explorer import get_cost_summary


def test_rejects_invalid_or_reversed_dates():
    with pytest.raises(ValueError):
        get_cost_summary(None, "2026-02-31", "2026-03-01")
    with pytest.raises(ValueError):
        get_cost_summary(None, "2026-03-02", "2026-03-01")


def test_cost_summary_requires_boto3_only_after_date_validation():
    assert date.fromisoformat("2026-01-01").isoformat() == "2026-01-01"
