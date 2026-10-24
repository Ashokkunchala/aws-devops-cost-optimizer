import pytest

from cost_optimizer.cost_explorer import get_cost_summary, summarize_cost_results


def test_rejects_invalid_or_reversed_dates():
    with pytest.raises(ValueError):
        get_cost_summary(None, "2026-02-31", "2026-03-01")
    with pytest.raises(ValueError):
        get_cost_summary(None, "2026-03-02", "2026-03-01")


def test_aggregates_monthly_costs_by_service():
    results = [
        {"Groups": [
            {"Keys": ["Amazon EC2"], "Metrics": {"UnblendedCost": {"Amount": "10.25", "Unit": "USD"}}},
            {"Keys": ["Amazon S3"], "Metrics": {"UnblendedCost": {"Amount": "2.00", "Unit": "USD"}}},
        ]},
        {"Groups": [
            {"Keys": ["Amazon EC2"], "Metrics": {"UnblendedCost": {"Amount": "4.75", "Unit": "USD"}}},
        ]},
    ]
    summary = summarize_cost_results(results, "2026-01-01", "2026-03-01")
    assert summary["total_actual_cost"] == 17.0
    assert summary["by_service"][0] == {"service": "Amazon EC2", "amount": 15.0, "currency": "USD"}
    assert summary["end_date_exclusive"] == "2026-03-01"
    assert "not projected savings" in summary["note"]


def test_refuses_mixed_currencies():
    results = [{"Groups": [
        {"Keys": ["Service A"], "Metrics": {"UnblendedCost": {"Amount": "1", "Unit": "USD"}}},
        {"Keys": ["Service B"], "Metrics": {"UnblendedCost": {"Amount": "2", "Unit": "EUR"}}},
    ]}]
    with pytest.raises(RuntimeError, match="mixed currencies"):
        summarize_cost_results(results, "2026-01-01", "2026-02-01")
