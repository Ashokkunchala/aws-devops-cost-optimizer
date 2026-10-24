# Roadmap

## Phase 1 — local rules and reports
- Synthetic JSON, deterministic review findings, report schema, tests, and CI.

## Phase 2 — AWS inventory
- Read-only regional EC2/EBS inventory through Boto3.
- Least-privilege IAM and credential guidance.

## Phase 3 — billing-aware estimates
- Support defined Cost Explorer exports and CUR/Athena result schemas.
- Track currency, region, usage period, and price source.
- Separate estimates from observed billed cost.

## Phase 4 — utilization recommendations
- Configurable CloudWatch lookback windows.
- Explain metric coverage and missing data.
- Evidence thresholds and workload exclusions.

## Phase 5 — guarded automation
- Dry-run, allowlists, environment protection, human approval, audit trail.
- Separate remediation permissions from scanner role.
- Recovery and rollback guidance.
