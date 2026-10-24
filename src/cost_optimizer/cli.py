"""CLI for synthetic fixtures and read-only AWS inventory scans."""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cost_optimizer.aws_inventory import collect_all_regions, collect_inventory
from cost_optimizer.cost_explorer import get_cost_summary
from cost_optimizer.cost_lab import audit_integration_gaps, compare_architectures, environment_blueprint
from cost_optimizer.dashboard import render_html
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


def _write_report(
    payload: dict[str, Any], args: argparse.Namespace, *, source_mode: str
) -> dict[str, Any]:
    payload["cpu_low_threshold_percent"] = args.cpu_low_threshold
    payload["generated_at"] = datetime.now(UTC).isoformat()
    report = build_report(payload, analyze_inventory(payload))
    report["source_mode"] = source_mode
    report["scan_metadata"] = {
        "generated_at": report["generated_at"],
        "region": payload.get("region"),
        "account_id": payload.get("account_id"),
        "identity_arn": payload.get("identity_arn"),
        "ec2_instances_scanned": len(payload.get("ec2_instances", [])),
        "ebs_volumes_scanned": len(payload.get("ebs_volumes", [])),
        "is_synthetic": source_mode == "local_fixture",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.html_output:
        args.html_output.parent.mkdir(parents=True, exist_ok=True)
        args.html_output.write_text(render_html(report), encoding="utf-8")
    print(
        f"[{report['generated_at']}] mode={source_mode} region={payload.get('region', 'n/a')} "
        f"account={payload.get('account_id', 'n/a')} "
        f"ec2={len(payload.get('ec2_instances', []))} "
        f"ebs={len(payload.get('ebs_volumes', []))} findings={len(report.get('findings', []))}"
    )
    print(f"JSON report: {args.output}")
    if args.html_output:
        print(f"HTML dashboard: {args.html_output}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read-only AWS cost optimizer. Live scans are snapshots; no resource mutations."
    )
    source = parser.add_mutually_exclusive_group(required=False)
    source.add_argument("--input", type=Path, help="Local JSON fixture (synthetic/demo mode).")
    source.add_argument("--aws", action="store_true", help="Collect read-only AWS inventory.")
    source.add_argument("--compare-architectures", nargs=2, type=Path, metavar=("CURRENT_JSON", "ALTERNATIVE_JSON"), help="Compare two architecture cost models (all monthly components required for a savings delta).")
    source.add_argument("--environment-blueprint", choices=["dev", "test", "staging", "production"], help="Print low-cost design guidance for an environment.")
    source.add_argument("--integration-audit", nargs=2, type=Path, metavar=("INVENTORY_JSON", "BILLING_JSON"), help="Compare discovered/integrated service families with Cost Explorer service rows.")
    parser.add_argument("--profile", help="AWS CLI profile name for AWS mode.")
    parser.add_argument("--all-regions", action="store_true", help="Scan all regions returned by the AWS EC2 region catalog.")
    parser.add_argument("--region", default="ap-south-1", help="AWS region (default: ap-south-1).")
    parser.add_argument("--lookback-days", type=int, default=14,
                        help="Hourly CloudWatch CPU lookback (1-90 days).")
    parser.add_argument("--cpu-low-threshold", type=float, default=5.0,
                        help="Flag CPU averages at or below this percentage (default: 5).")
    parser.add_argument("--cost-explorer", action="store_true",
                        help="Include actual AWS Cost Explorer costs (read-only).")
    parser.add_argument("--cost-start-date", help="Cost Explorer start date, YYYY-MM-DD inclusive.")
    parser.add_argument("--cost-end-date", help="Cost Explorer end date, YYYY-MM-DD exclusive.")
    parser.add_argument("--watch", action="store_true",
                        help="Repeat AWS inventory scans until Ctrl+C; refresh interval defaults to 300 seconds.")
    parser.add_argument("--refresh-seconds", type=int, default=300,
                        help="Interval between --watch scans (minimum 60 seconds; default: 300).")
    parser.add_argument("--output", type=Path, default=Path("reports/cost-report.json"))
    parser.add_argument("--html-output", type=Path, help="Self-contained HTML dashboard output path.")
    args = parser.parse_args()
    if not any((args.input, args.aws, args.compare_architectures, args.environment_blueprint, args.integration_audit)):
        parser.error("Choose --input, --aws, --compare-architectures, --environment-blueprint, or --integration-audit")

    if args.compare_architectures:
        result = compare_architectures(_load_json(args.compare_architectures[0]), _load_json(args.compare_architectures[1]))
        print(json.dumps(result, indent=2))
        return
    if args.environment_blueprint:
        print(json.dumps(environment_blueprint(args.environment_blueprint), indent=2))
        return
    if args.integration_audit:
        inventory = _load_json(args.integration_audit[0])
        billing = _load_json(args.integration_audit[1])
        result = audit_integration_gaps(inventory, billing.get("by_service", []))
        print(json.dumps(result, indent=2))
        return

    if not 0.0 <= args.cpu_low_threshold <= 100.0:
        parser.error("--cpu-low-threshold must be between 0 and 100")
    if args.aws and not 1 <= args.lookback_days <= 90:
        parser.error("--lookback-days must be between 1 and 90")
    if args.watch and not args.aws:
        parser.error("--watch can only be used with --aws")
    if args.watch and args.refresh_seconds < 60:
        parser.error("--refresh-seconds must be at least 60 to avoid excessive AWS API calls")
    if args.cost_explorer:
        if not args.aws:
            parser.error("--cost-explorer can only be used with --aws")
        if not args.cost_start_date or not args.cost_end_date:
            parser.error("--cost-explorer requires --cost-start-date and --cost-end-date")
    elif args.cost_start_date or args.cost_end_date:
        parser.error("Provide both cost dates together with --cost-explorer")

    if not args.aws:
        payload = _load_json(args.input)
        payload.setdefault("mode", "local_fixture")
        _write_report(payload, args, source_mode="local_fixture")
        print("NOTE: This is synthetic fixture data, not a live AWS scan.")
        return

    def scan_once() -> None:
        if args.all_regions:
            payload = collect_all_regions(args.profile, args.lookback_days)
            if payload.get("region_scan_errors"):
                print("WARNING: Some regions could not be scanned; inspect JSON report.")
        else:
            payload = collect_inventory(args.profile, args.region, args.lookback_days)
        payload["dashboard_refresh_seconds"] = args.refresh_seconds if args.watch else None
        if args.cost_explorer:
            payload["cost_explorer"] = get_cost_summary(
                args.profile, args.cost_start_date, args.cost_end_date
            )
        _write_report(payload, args, source_mode="aws_read_only")

    if not args.watch:
        scan_once()
        return

    print(f"Watch mode active: refreshing every {args.refresh_seconds}s. Press Ctrl+C to stop.")
    try:
        while True:
            started = time.monotonic()
            scan_once()
            time.sleep(max(0, args.refresh_seconds - (time.monotonic() - started)))
    except KeyboardInterrupt:
        print("\nWatch mode stopped. Last report files are preserved.")


if __name__ == "__main__":
    main()
