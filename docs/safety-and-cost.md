# Safety and Cost Guardrails

1. Start with local synthetic fixtures; this mode makes no AWS calls.
2. AWS inventory mode is read-only.
3. Never print credentials or environment variables.
4. Do not invent savings amounts. Estimates require verified region, service, usage, pricing, discounts, and commitment data.
5. A recommendation is not permission to act.
6. No automatic deletion or stopping is included.
7. Avoid publishing account-specific reports or sensitive inventory.

## Cost notes

- Inventory uses EC2 Describe APIs and creates no AWS resources.
- Cost Explorer and CUR/Athena have separate setup and possible charges; they are not enabled here.
- Terraform is never applied automatically. Inspect plans.
- Do not create NAT Gateways, EKS, load balancers, databases, or always-on compute just to demonstrate the tool.

Any future remediation should require dry-run output, resource allowlists, environment protection, human approval, audit trail, pre-change evidence, and recovery guidance. Check ownership, backups, dependencies, maintenance windows, and retention before acting.
