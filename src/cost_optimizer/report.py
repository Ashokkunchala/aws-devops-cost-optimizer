"""Report rendering helpers."""

from datetime import UTC, datetime
from typing import Any


def build_report(payload: dict[str, Any], findings: list[dict[str, Any]]) -> dict[str, Any]:
    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": payload.get("mode", "local_fixture"),
        "region": payload.get("region"),
        "summary": {
            "ec2_instances_scanned": len(payload.get("ec2_instances", [])),
            "ebs_volumes_scanned": len(payload.get("ebs_volumes", [])),
            "findings": len(findings),
            "estimated_monthly_savings": None,
            "estimate_note": (
                "Not calculated: validated region-specific pricing and workload data are required. "
                "Recommendations are not guaranteed savings."
            ),
        },
        "findings": findings,
        "safety": {"mutations_performed": False, "human_review_required": True},
    }
    if payload.get("cost_explorer"):
        report["cost_explorer"] = payload["cost_explorer"]
    return report
