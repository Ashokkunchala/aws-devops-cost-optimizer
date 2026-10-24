# Safety and Cost Guardrails

1. Start with local synthetic fixtures; no AWS calls are made in this mode.
2. AWS inventory mode is read-only.
3. Never print credentials or environment variables.
4. Do not invent savings figures. Estimate only with validated region, service, usage, pricing, discounts, and commitment data.
5. Recommendations are not permission to act.
6. No automatic deletion or stopping is included.
7. Remove account-specific reports and sensitive inventory from public artifacts.

## Cost notes

- Inventory uses EC2 Describe APIs and does not create AWS resources.
- Cost Explorer and CUR/Athena integrations have separate permissions, setup and possible charges; they are not enabled in this starter.
- Terraform is never applied automatically. Inspect plans.
- Do not create NAT Gateways, EKS, load balancers, databases, or always-on compute just to demonstrate this tool.

Before any future remediation, require dry-run output, resource allowlists, environment exclusion, human approval, a change record, audit log, pre-change evidence, and recovery guidance. Validate ownership, backups, dependencies, maintenance windows, and retention.
