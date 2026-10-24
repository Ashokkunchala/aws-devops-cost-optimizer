"""Command-line interface for local fixtures and read-only AWS inventory."""

import argparse
import json
from pathlib import Path
from typing import Any

from cost_optimizer.aws_inventory import collect_inventory
from cost_optimizer.report import build_report
from cost_optimizer.rules import analyze_inventory


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Unable to read valid JSON from {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("Input JSON root must be an object.")
    for key in ("ec2_instances", "ebs_volumes"):
        if key in payload and not isinstance(payload[key], list):
            raise SystemExit(f"Input field {key!r} must be a list.")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only AWS cost optimization inventory.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Local JSON inventory fixture.")
    source.add_argument("--aws", action="store_true", help="Collect read-only AWS inventory.")
    parser.add_argument("--profile", help="AWS CLI profile name for AWS mode.")
    parser.add_argument("--region", default="ap-south-1", help="AWS region (default: ap-south-1).")
    parser.add_argument(
        "--lookback-days", type=int, default=14,
        help="Hourly CloudWatch CPU lookback for AWS mode (1-90 days; default: 14).",
    )
    parser.add_argument("--cpu-low-threshold", type=float, default=5.0,
                        help="Flag CPU averages at or below this percentage (default: 5).")
    parser.add_argument("--output", type=Path, default=Path("reports/cost-report.json"))
    args = parser.parse_args()
    if not 0.0 <= args.cpu_low_threshold <= 100.0:
        parser.error("--cpu-low-threshold must be between 0 and 100")
    if args.aws:
        if not 1 <= args.lookback_days <= 90:
            parser.error("--lookback-days must be between 1 and 90")
        payload = collect_inventory(args.profile, args.region, args.lookback_days)
    else:
        payload = _load_json(args.input)
        payload.setdefault("mode", "local_fixture")
    payload["cpu_low_threshold_percent"] = args.cpu_low_threshold
    findings = analyze_inventory(payload)
    report = build_report(payload, findings)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
