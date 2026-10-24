"""Optional read-only AWS inventory collector. Never mutates AWS resources."""

from __future__ import annotations

from typing import Any


def collect_inventory(profile: str | None, region: str) -> dict[str, Any]:
    """Collect EC2 instance and EBS volume metadata in one region."""
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError as exc:
        raise RuntimeError(
            'AWS mode requires optional dependencies. Install with: pip install -e ".[aws]"'
        ) from exc

    session = boto3.Session(profile_name=profile, region_name=region)
    ec2 = session.client("ec2")
    instances: list[dict[str, Any]] = []
    volumes: list[dict[str, Any]] = []

    try:
        for page in ec2.get_paginator("describe_instances").paginate():
            for reservation in page.get("Reservations", []):
                for item in reservation.get("Instances", []):
                    tags = {tag["Key"]: tag.get("Value", "") for tag in item.get("Tags", [])}
                    instances.append({
                        "instance_id": item.get("InstanceId", "unknown"),
                        "state": item.get("State", {}).get("Name", "unknown"),
                        "instance_type": item.get("InstanceType"),
                        "tags": tags,
                    })

        for page in ec2.get_paginator("describe_volumes").paginate():
            for item in page.get("Volumes", []):
                tags = {tag["Key"]: tag.get("Value", "") for tag in item.get("Tags", [])}
                volumes.append({
                    "volume_id": item.get("VolumeId", "unknown"),
                    "state": item.get("State", "unknown"),
                    "size_gib": item.get("Size"),
                    "volume_type": item.get("VolumeType"),
                    "tags": tags,
                })
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"AWS read-only inventory failed in region {region}: {exc}") from exc

    return {
        "mode": "aws_read_only",
        "region": region,
        "ec2_instances": instances,
        "ebs_volumes": volumes,
    }
