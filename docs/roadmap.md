# Roadmap

## Phase 1 — local rules and reports
- Synthetic JSON input, deterministic review findings, report schema, unit tests, CI.

## Phase 2 — AWS inventory
- Read-only regional EC2/EBS inventory through Boto3.
- Minimal IAM policy and credential guidance.
- Pagination and error handling.

## Phase 3 — billing-aware estimates
- Define supported schemas for Cost Explorer exports and CUR/Athena results.
- Track currency, region, period, and price source.
- Separate estimates from observed billed cost and validate against fixtures.

## Phase 4 — utilization recommendations
- Configurable CloudWatch lookback windows.
- Explain metric coverage and missing data.
- Use evidence thresholds and workload exclusions.

## Phase 5 — guarded automation
- Dry-run first; allowlists and environment protection.
- Human approval and audit trail.
- Separate remediation role and permissions.
- Document recovery and rollback.
