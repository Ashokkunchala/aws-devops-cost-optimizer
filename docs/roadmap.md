# Delivery status and roadmap

## Implemented in this release
- Local synthetic JSON input and deterministic findings.
- Read-only EC2/EBS inventory.
- Hourly CloudWatch CPU summaries over a bounded lookback.
- Optional Cost Explorer actual unblended cost by service.
- JSON reports and self-contained HTML reports.
- Unit tests and GitHub Actions CI on Python 3.11 and 3.12.
- Optional Terraform monthly budget-alert example (never auto-applied).

## Next recommended work
1. Add validated CUR CSV/Parquet schemas and reconciliation against Cost Explorer.
2. Add pricing-aware estimates only when region, instance family, operating system, tenancy, usage, discount, and commitment data are known.
3. Add S3 inventory and lifecycle review with pagination, request-volume warnings, and object-retention safeguards.
4. Add a web dashboard only if a hosting target and authentication model are selected.
5. If remediation is ever added, use dry-run, allowlists, explicit human approval, audit trail, and recovery procedures.

No remediation or cloud resource provisioning is part of the current scanner.
