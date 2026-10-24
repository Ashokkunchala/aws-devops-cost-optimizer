"""Command-line interface."""

from __future__ import annotations

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
    parser = argparse.ArgumentParser(
        description="Read-only AWS cost optimization inventory and report tool."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Local JSON inventory fixture.")
    source.add_argument("--aws", action="store_true", help="Collect read-only AWS inventory.")
    parser.add_argument("--profile", help="AWS CLI profile name for AWS mode.")
    parser.add_argument("--region", default="ap-south-1", help="AWS region (default: ap-south-1).")
    parser.add_argument("--output", type=Path, default=Path("reports/cost-report.json"))
    args = parser.parse_args()

    if args.aws:
        payload = collect_inventory(args.profile, args.region)
    else:
        payload = _load_json(args.input)
        payload.setdefault("mode", "local_fixture")

    findings = analyze_inventory(payload)
    report = build_report(payload, findings)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
