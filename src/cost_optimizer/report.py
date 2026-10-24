"""Report rendering helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_report(payload: dict[str, Any], findings: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": payload.get("mode", "local_fixture"),
        "region": payload.get("region"),
        "summary": {
            "ec2_instances_scanned": len(payload.get("ec2_instances", [])),
            "ebs_volumes_scanned": len(payload.get("ebs_volumes", [])),
            "findings": len(findings),
            "estimated_monthly_savings": None,
            "estimate_note": (
                "Not calculated: validated, region-specific pricing and workload data are required. "
                "Do not treat recommendations as guaranteed savings."
            ),
        },
        "findings": findings,
        "safety": {"mutations_performed": False, "human_review_required": True},
    }
