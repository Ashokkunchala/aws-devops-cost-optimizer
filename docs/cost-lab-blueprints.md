# Cost Lab: compare architectures before deploying

This project is intended to teach cost reduction by comparing **two or more deployable architectures** for the same workload, showing cost components, what is included or missing, and the trade-offs. It must not imply that a cheaper architecture is production-safe without workload requirements.

## The product experience

For each workload, the user selects an environment (dev, test, staging, production), expected uptime, request/traffic level, data size, availability target, RTO/RPO, and whether it is public-facing. The tool produces:

1. A cost-component map (compute, database, storage, load balancing, NAT/data transfer, logs/metrics, DNS, backups, security, and support).
2. Two architecture cards: current/reference design and a lower-cost alternative.
3. A monthly estimate with assumptions, AWS region, pricing source/date, free-tier eligibility caveat, usage range, and unknown/unpriced items.
4. An integration-gap audit: enabled services/resources that do not appear in inventory or billing, resources without environment/owner tags, and billing line items that cannot be mapped to discovered resources.
5. A risk and parity comparison (availability, resilience, security, performance, operational burden, backup/restore).
6. A change plan with estimated delta, prerequisites, rollback, and approval. No change executes by default.
7. Post-change measurement comparing the actual AWS bill with a baseline; realized savings must be measured, not assumed.

## Cost component checklist

- Compute: EC2 instance-hours, EBS root/data disks, snapshots, Elastic IPs, load balancers, ECS/EKS control plane or Fargate tasks, Lambda requests/runtime.
- Database: RDS/Aurora instance-hours, storage, I/O, backups, replicas, NAT/data transfer.
- Network: NAT Gateway hours and processed GB, interface VPC endpoints per AZ and GB, public IPv4 addresses, cross-AZ/cross-region transfer, load balancers, CloudFront/data egress.
- Storage: S3 storage class, requests, retrieval, lifecycle transitions, replication, EBS volumes and snapshots, EFS storage/access.
- Observability/security: CloudWatch logs ingest/storage/queries, metrics/alarms, traces, Config rules/recording, GuardDuty data volume, Security Hub plan, WAF requests/rules, KMS keys/requests.
- Other: Route 53 hosted zones/queries, backup storage, secrets, container registries/image storage, support plan, Marketplace/SaaS, taxes/credits/discounts.

A service missing from inventory is not necessarily absent from the bill. Some services are global, regional, account-level, serverless, shared, marketplace-billed, or represented only in billing line items. Never label a resource as safe to remove just because a direct inventory API does not return it.

## Environment blueprints

These are starting patterns, not guaranteed prices. Estimate using the actual region, price list, traffic, data, retention, and uptime before deployment.

### Dev
- Prefer local containers or a developer workstation for unit tests.
- For cloud integration tests: short-lived, on-demand EC2 or a small serverless endpoint; deploy on demand and tear down with TTL automation.
- Use SQLite/local containers for disposable tests; if managed database compatibility is needed, start/stop a supported non-production RDS instance when appropriate, or use a short-lived database.
- One small private test workload may use no load balancer if a public endpoint is unnecessary.
- Use low log retention and limited non-production data; preserve security/audit logs required by policy.
- Never leave NAT Gateways, idle load balancers, public IPv4 addresses, databases, or test clusters running just for convenience.

### Test / CI
- Use ephemeral runners/containers, caching, and parallelism limits; build once and promote artifacts.
- Prefer Lambda/API Gateway or a small single-instance test service when compatible; do not use EKS just to host a tiny demo.
- Provision test dependencies on demand and clean them up with TTLs.
- Use Spot for interruptible test workers only when retries/checkpointing are safe.

### Staging
- Match production's important runtime, deployment, networking, and data migration characteristics, but scale down capacity and nonessential retention where testing goals permit.
- Use one instance/one AZ only when staging's explicit availability objective allows it; document reduced resilience.
- Avoid production-scale replicas, always-on load generators, and duplicate expensive telemetry.
- Keep security, authentication, backup/restore, and release validation realistic.

### Production
- Select architecture from SLO, peak traffic, RTO/RPO, compliance, and support needs—not price alone.
- Consider Graviton/right-sizing, autoscaling, Savings Plans only for stable usage, Spot for fault-tolerant workers, serverless for bursty workloads, and caching/CDN where appropriate.
- Use multi-AZ/replicas and backups when availability/data durability requires them. Do not remove them simply to chase zero cost.
- Set budgets/anomaly alerts, log retention, ownership/environment/cost-centre tags, and disaster recovery tests.

## Free or near-zero-cost options: caveats

- Local development and local containers often avoid AWS runtime charges, but still use workstation/electricity and do not validate all managed-service behaviours.
- AWS Free Tier / free offers depend on account eligibility, service, region, quota, and offer period. Overages, public IPv4, data transfer, storage, logs, and ancillary resources may still cost money.
- Lambda, S3, DynamoDB, API Gateway, CloudFront, and other serverless services are pay-per-use, not universally free.
- NAT Gateway, managed Kubernetes, load balancers, managed databases, VPC interface endpoints, logs, and public IPv4 can create fixed or usage-based charges even when application traffic is low.
- Spot is cheaper but interruptible. Do not use it for workloads that cannot tolerate interruption.
- No cloud resource is labelled “$0” unless the estimate demonstrates zero billable usage under the stated assumptions and free offer, and states the offer expiry/limits.

## Real-time vs billing latency

- Resource inventory and CloudWatch metrics can be polled on a short interval, but are not a billing feed.
- Cost Explorer / CUR billing records are delayed and may be adjusted. Use billing data for reconciliation and actual savings measurement, not second-by-second feedback.
- The dashboard should show separate timestamps for inventory, metrics, price data, and billing data.
- A real-time-looking dashboard must never imply that a five-minute inventory scan makes the AWS bill real-time.

## Safe remediation lifecycle

1. Detect and show evidence.
2. Estimate the savings range and confidence; display unpriced items.
3. Compare architecture and operational/security trade-offs.
4. Generate a dry-run plan.
5. Require approval for changes; use environment allowlists and maintenance windows.
6. Record who approved, what changed, before/after configuration, and rollback instructions.
7. Verify health and cost after change; distinguish estimated, pending, and realized savings.

Do not auto-delete storage, snapshots, networking, logging, security controls, or production resources based only on cost signals.
