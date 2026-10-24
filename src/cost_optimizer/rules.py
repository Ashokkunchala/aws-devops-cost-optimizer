"""Deterministic, report-only optimization rules for normalized inventory."""

from __future__ import annotations

from typing import Any


def analyze_inventory(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return findings from normalized inventory without mutating resources."""
    findings: list[dict[str, Any]] = []
    for instance in payload.get("ec2_instances", []):
        instance_id = str(instance.get("instance_id", "unknown"))
        state = str(instance.get("state", "unknown")).lower()
        tags = instance.get("tags") or {}
        owner = tags.get("Owner") or tags.get("owner")
        if state == "stopped":
            findings.append({
                "resource_type": "ec2_instance", "resource_id": instance_id,
                "severity": "info",
                "finding": "Stopped instance: review attached storage and operational need",
                "evidence": {"state": state},
                "recommendation": (
                    "Confirm the instance is intentionally stopped. Review attached EBS volumes, "
                    "snapshots, retention requirements, and restart dependencies."
                ),
                "estimate_status": "not_calculated", "owner": owner,
            })
        elif state == "running" and not owner:
            findings.append({
                "resource_type": "ec2_instance", "resource_id": instance_id,
                "severity": "low", "finding": "Running instance missing an Owner tag",
                "evidence": {"state": state, "owner_tag_present": False},
                "recommendation": (
                    "Add ownership and environment tags to improve accountability and cost "
                    "allocation. Do not stop or resize based on missing tags alone."
                ),
                "estimate_status": "not_calculated", "owner": None,
            })
    for volume in payload.get("ebs_volumes", []):
        volume_id = str(volume.get("volume_id", "unknown"))
        state = str(volume.get("state", "unknown")).lower()
        size_gib = volume.get("size_gib")
        tags = volume.get("tags") or {}
        if state == "available":
            findings.append({
                "resource_type": "ebs_volume", "resource_id": volume_id,
                "severity": "medium", "finding": "Unattached EBS volume candidate",
                "evidence": {"state": state, "size_gib": size_gib},
                "recommendation": (
                    "Check attachment history, backups, retention, disaster recovery, and whether "
                    "the volume is intentionally reserved before considering removal."
                ),
                "estimate_status": "not_calculated",
                "owner": tags.get("Owner") or tags.get("owner"),
            })
    return findings
