# AWS DevOps Cost Optimizer

A free-first, safety-first FinOps toolkit for AWS and DevOps teams. It helps identify potential waste, generate reviewable reports, and build repeatable cost-control practices without automatically changing production infrastructure.

> **Default posture: read-only.** The initial scanner inventories EC2/EBS resources and reports candidates for human review. It does not stop, resize, detach, or delete resources. Cost estimates must be checked against your account pricing, discounts, region, and usage.

## Goals

- Find likely optimization opportunities for EC2 and EBS.
- Report candidates with evidence and caveats.
- Run locally with synthetic data and no AWS resources.
- Use least-privilege credentials, tests, and CI.
- Add billing-data analysis later through explicit Cost Explorer or CUR inputs.
- Keep remediation separate and approval-gated.

## Quick start (no AWS account needed)

Requirements: Python 3.11+.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
python -m cost_optimizer --input examples/sample_inventory.json --output reports/sample-report.json
```

The sample input is synthetic. No AWS calls are made in local mode.

## Read-only AWS scan

1. Configure AWS credentials using an approved local profile or IAM Identity Center. Never put keys in source files.
2. Start with the narrow read-only policy in [docs/iam-read-only.md](docs/iam-read-only.md).
3. Run a regional inventory:

```bash
aws sts get-caller-identity --profile cost-audit
python -m cost_optimizer --aws --profile cost-audit --region ap-south-1 --output reports/aws-report.json
```

AWS mode uses EC2 Describe APIs only. Review AWS service pricing and API limits before repeated scans. Never use root credentials.

## Report fields

Findings include resource ID, type, severity, evidence, recommendation, and estimate status. Savings amounts are **not fabricated**: estimates remain unavailable unless validated pricing and usage data are supplied. Recommendations are not proof that a resource is safe to change.

## Project layout

- `src/cost_optimizer/` — CLI, rules, AWS read-only collector, report generator.
- `examples/` — synthetic input for testing without AWS.
- `tests/` — deterministic tests; no live cloud calls.
- `docs/` — IAM, safety, roadmap.
- `terraform/` — optional budget-alert example, not applied automatically.
- `.github/workflows/ci.yml` — test and lint checks.

## Cost safety

- Do not deploy Terraform until you inspect the plan and understand the current service pricing.
- AWS Budgets and other billing features may have eligibility, usage, or pricing constraints; verify before use.
- The Terraform example is optional and does not create compute or networking.
- Never enable destructive remediation based on one metric or a generic recommendation.
- Validate ownership, criticality, dependencies, backups, maintenance windows, and approvals before changing resources.

## Roadmap

1. [x] Local JSON input, rule engine, JSON report, and tests.
2. [x] Read-only EC2/EBS inventory collector.
3. [x] CI for tests and lint.
4. [x] Optional budget-alert Terraform example.
5. [ ] Parse Cost Explorer exports / CUR Athena results.
6. [ ] Pricing-aware estimates with region and effective dates.
7. [ ] Utilization recommendations using a configurable historical window.
8. [ ] Approval-gated remediation with dry-run, allowlists, audit records, and recovery guidance.

## License

MIT — see [LICENSE](LICENSE).
