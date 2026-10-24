"""Read-only AWS Cost Explorer queries."""

from __future__ import annotations

from datetime import date
from typing import Any


def get_cost_summary(
    profile: str | None, start_date: str, end_date: str, region: str | None = None
) -> dict[str, Any]:
    """Fetch actual unblended cost grouped by service.

    Cost Explorer's End date is exclusive. Dates must be ISO YYYY-MM-DD.
    """
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as exc:
        raise ValueError("Cost Explorer dates must use YYYY-MM-DD format") from exc
    if end <= start:
        raise ValueError("end_date must be later than start_date (exclusive)")

    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError as exc:
        raise RuntimeError(
            'Cost Explorer mode requires optional dependencies. Install with: pip install -e ".[aws]"'
        ) from exc

    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client("ce", region_name="us-east-1")
    params: dict[str, Any] = {
        "TimePeriod": {"Start": start.isoformat(), "End": end.isoformat()},
        "Granularity": "MONTHLY",
        "Metrics": ["UnblendedCost"],
        "GroupBy": [{"Type": "DIMENSION", "Key": "SERVICE"}],
    }
    results: list[dict[str, Any]] = []
    try:
        while True:
            response = client.get_cost_and_usage(**params)
            results.extend(response.get("ResultsByTime", []))
            token = response.get("NextPageToken")
            if not token:
                break
            params["NextPageToken"] = token
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Cost Explorer query failed: {exc}") from exc

    by_service: dict[str, dict[str, Any]] = {}
    total = 0.0
    currency = "USD"
    for period in results:
        for group in period.get("Groups", []):
            service = group.get("Keys", ["Unknown service"])[0]
            metric = group.get("Metrics", {}).get("UnblendedCost", {})
            amount = float(metric.get("Amount", "0"))
            unit = metric.get("Unit", currency)
            if unit != currency and total != 0:
                raise RuntimeError("Cost Explorer returned mixed currencies; refusing to combine.")
            currency = unit
            total += amount
            entry = by_service.setdefault(service, {"amount": 0.0, "currency": unit})
            entry["amount"] += amount

    services = [
        {"service": name, "amount": round(item["amount"], 6), "currency": item["currency"]}
        for name, item in sorted(by_service.items(), key=lambda pair: pair[1]["amount"], reverse=True)
    ]
    return {
        "source": "AWS Cost Explorer",
        "metric": "UnblendedCost",
        "start_date": start.isoformat(),
        "end_date_exclusive": end.isoformat(),
        "granularity": "MONTHLY",
        "currency": currency,
        "total_actual_cost": round(total, 6),
        "by_service": services,
        "note": (
            "Actual unblended charges returned by Cost Explorer, not projected savings. "
            "Data may be delayed and may not equal the final invoice."
        ),
    }
