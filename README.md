# AWS DevOps Cost Optimizer

A free-first, safety-first FinOps toolkit for AWS and DevOps teams. It inventories EC2/EBS, reviews CPU utilization, optionally queries actual AWS Cost Explorer charges, and creates JSON plus self-contained HTML reports.

**Default posture: read-only.** It never stops, resizes, detaches, or deletes resources. It does not invent savings estimates.

## Features
- Local synthetic mode for learning and tests without AWS access.
- Regional EC2/EBS inventory with unattached-volume and ownership-tag findings.
- Hourly CloudWatch CPU averages/maxima for running instances over a bounded 1–90 day window.
- Optional AWS Cost Explorer actual UnblendedCost by service.
- JSON output and optional HTML report with escaped resource values.
- Least-privilege guidance, unit tests, and GitHub Actions CI.
- Optional Terraform monthly budget alert example, never auto-applied.\n- Non-root Docker image for local or approved read-only AWS scans.

## Quick start without AWS

Requires Python 3.11+.

    python -m venv .venv
    # Linux/macOS: source .venv/bin/activate
    # Windows PowerShell: .\.venv\Scripts\Activate.ps1
    python -m pip install -e ".[dev]"
    pytest
    python -m cost_optimizer --input examples/sample_inventory.json --output reports/sample-report.json --html-output reports/sample-report.html

The sample input is synthetic. No AWS calls are made in local mode. The generated dashboard displays a prominent demo-data warning; do not interpret sample resource IDs or counts as live account data.

## Read-only AWS inventory

Configure an approved AWS CLI profile or IAM Identity Center role. Do not put access keys in source files.

    aws sts get-caller-identity --profile cost-audit
    python -m pip install -e ".[aws]"
    python -m cost_optimizer --aws --profile cost-audit --region ap-south-1 --lookback-days 14 --output reports/aws-report.json --html-output reports/aws-report.html

### Multi-region scan\n\nTo avoid missing resources outside Mumbai, scan all regions returned by the AWS EC2 region catalog:\n\n    python -m cost_optimizer --aws --profile cost-audit --all-regions --lookback-days 1 --output reports/aws-all-regions.json --html-output reports/aws-all-regions.html\n\nThe report includes region-level scan errors rather than silently treating failed regions as empty. Review those errors and confirm that the profile can describe resources in each region. Billing data from Cost Explorer is account-level, not a regional inventory total.\n\n### Near-real-time refresh mode\n\nFor a repeatedly refreshed regional inventory snapshot, use `--watch`. It rewrites the JSON and HTML files on each scan; refresh the browser page to see the latest snapshot. The minimum interval is 60 seconds, with a default of 300 seconds. Use a 5-minute or longer interval for normal use; EC2 basic monitoring is typically delivered in 5-minute periods and API results are not instantaneous. This is polling, not a streaming feed. Press Ctrl+C to stop.\n\n    python -m cost_optimizer --aws --profile cost-audit --all-regions --lookback-days 1 --watch --refresh-seconds 300 --output reports/aws-live.json --html-output reports/aws-live.html\n\nThe dashboard shows the AWS account ID, region, scan timestamp, and whether data is synthetic or live. Regional EC2/EBS inventory is scoped to the selected region. Cost Explorer billing is account-level, may be delayed, and must not be mistaken for regional spend. An empty inventory is valid if the selected account/region has no visible resources. Verify the identity with `aws sts get-caller-identity --profile cost-audit` before trusting a report.\n\n## Include actual billing costs

Enable the optional Cost Explorer query and provide ISO dates. Start is inclusive and end is exclusive, matching the AWS API.

    python -m cost_optimizer --aws --profile cost-audit --region ap-south-1 --lookback-days 14 --cost-explorer --cost-start-date 2026-10-01 --cost-end-date 2026-11-01 --output reports/aws-cost-report.json --html-output reports/aws-cost-report.html

The billing query requires the IAM action ce:GetCostAndUsage. Cost Explorer is queried in us-east-1. Returned figures are actual unblended costs as currently reported by Cost Explorer, not guaranteed final invoice amounts or savings; data may be delayed. Review AWS pricing and account permissions before use.

## Findings and limitations
- A stopped instance is a review prompt; its EBS volumes and snapshots may still cost money.
- An unattached EBS volume may be intentional or required for recovery. Never delete it based on the finding alone.
- Low CPU is only a screening signal. Check memory, network, disk I/O, CPU credits, workload seasonality, autoscaling, and business schedules before resizing.
- Missing metrics are not treated as zero.
- Savings estimates remain null until supported by validated region-specific pricing, usage, discount, and commitment data.
- Reports may include resource IDs and inventory metadata. Keep them private; do not commit real-account reports.

## IAM

See docs/iam-read-only.md. Keep billing access optional and separate from inventory access if that better fits your security model.

## Project structure
- src/cost_optimizer/ — scanner, Cost Explorer query, rule engine, report generation.
- examples/ — synthetic fixtures.
- tests/ — unit tests; no live cloud calls.
- docs/ — safety and IAM guidance.
- terraform/budget-alert/ — optional budget notification example.\n- Dockerfile and docs/container-run.md — containerized CLI.

## Safety

No AWS infrastructure has to be created to run the scanner. Terraform is not applied by CI. Inspect any Terraform plan and current AWS pricing before opting into the budget example. There is no destructive remediation in this project.

## Roadmap

See docs/roadmap.md for delivery status and next work.

## License

MIT — see LICENSE.
