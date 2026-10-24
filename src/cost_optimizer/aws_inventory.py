"""Optional read-only AWS inventory collector; never mutates resources."""

from datetime import UTC, datetime, timedelta
from statistics import mean
from typing import Any


def _cpu_summary(cloudwatch: Any, instance_id: str, lookback_days: int) -> dict[str, Any]:
    """Get a bounded CPUUtilization summary from standard EC2 CloudWatch metrics."""
    end = datetime.now(UTC)
    start = end - timedelta(days=lookback_days)
    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start,
        EndTime=end,
        Period=3600,
        Statistics=["Average", "Maximum"],
    )
    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return {
            "cpu_average_percent": None,
            "cpu_max_percent": None,
            "cpu_datapoints": 0,
            "cpu_metric_status": "no_data",
        }
    averages = [float(point["Average"]) for point in datapoints if "Average" in point]
    maxima = [float(point["Maximum"]) for point in datapoints if "Maximum" in point]
    return {
        "cpu_average_percent": round(mean(averages), 2) if averages else None,
        "cpu_max_percent": round(max(maxima), 2) if maxima else None,
        "cpu_datapoints": len(datapoints),
        "cpu_metric_status": "available" if averages else "no_data",
    }


def collect_inventory(
    profile: str | None, region: str, lookback_days: int = 14
) -> dict[str, Any]:
    """Collect read-only EC2/EBS inventory and hourly CPU summaries in one region."""
    if not 1 <= lookback_days <= 90:
        raise ValueError("lookback_days must be between 1 and 90")
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError as exc:
        raise RuntimeError(
            'AWS mode requires optional dependencies. Install with: pip install -e ".[aws]"'
        ) from exc
    session = boto3.Session(profile_name=profile, region_name=region)
    ec2 = session.client("ec2")
    cloudwatch = session.client("cloudwatch")
    sts = session.client("sts")
    instances: list[dict[str, Any]] = []
    volumes: list[dict[str, Any]] = []
    try:
        identity = sts.get_caller_identity()
        for page in ec2.get_paginator("describe_instances").paginate():
            for reservation in page.get("Reservations", []):
                for item in reservation.get("Instances", []):
                    tags = {tag["Key"]: tag.get("Value", "") for tag in item.get("Tags", [])}
                    instance_id = item.get("InstanceId", "unknown")
                    state = item.get("State", {}).get("Name", "unknown")
                    entry: dict[str, Any] = {
                        "instance_id": instance_id,
                        "region": region,
                        "state": state,
                        "instance_type": item.get("InstanceType"),
                        "tags": tags,
                    }
                    if state == "running":
                        entry.update(_cpu_summary(cloudwatch, instance_id, lookback_days))
                    instances.append(entry)
        for page in ec2.get_paginator("describe_volumes").paginate():
            for item in page.get("Volumes", []):
                tags = {tag["Key"]: tag.get("Value", "") for tag in item.get("Tags", [])}
                volumes.append({
                    "volume_id": item.get("VolumeId", "unknown"),
                    "region": region,
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
        "account_id": identity.get("Account"),
        "identity_arn": identity.get("Arn"),
        "lookback_days": lookback_days,
        "ec2_instances": instances,
        "ebs_volumes": volumes,
    }



def collect_all_regions(profile: str | None, lookback_days: int = 14) -> dict[str, Any]:
    """Scan all regions returned by EC2's region catalog; record per-region failures."""
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError as exc:
        raise RuntimeError(
            'AWS mode requires optional dependencies. Install with: pip install -e ".[aws]"'
        ) from exc
    session = boto3.Session(profile_name=profile)
    regions = sorted(session.get_available_regions("ec2"))
    instances: list[dict[str, Any]] = []
    volumes: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    account_id = None
    identity_arn = None
    for region in regions:
        try:
            regional = collect_inventory(profile, region, lookback_days)
            account_id = account_id or regional.get("account_id")
            identity_arn = identity_arn or regional.get("identity_arn")
            instances.extend(regional.get("ec2_instances", []))
            volumes.extend(regional.get("ebs_volumes", []))
        except (RuntimeError, BotoCoreError, ClientError) as exc:
            errors.append({"region": region, "error": str(exc)})
    return {
        "mode": "aws_read_only",
        "region": "all-enabled-regions",
        "account_id": account_id,
        "identity_arn": identity_arn,
        "lookback_days": lookback_days,
        "regions_attempted": regions,
        "region_scan_errors": errors,
        "ec2_instances": instances,
        "ebs_volumes": volumes,
    }
