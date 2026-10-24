"""Architecture cost lab and inventory-vs-billing integration gap audit.

This module uses explicit user-supplied monthly component estimates. It never
pretends estimates are live AWS prices and never changes infrastructure.
"""
from __future__ import annotations

from typing import Any

COST_COMPONENTS = (
    "compute", "database", "storage", "load_balancing", "nat_and_endpoints",
    "data_transfer", "logs_and_metrics", "security", "backup", "dns", "support", "other",
)

ENVIRONMENT_GUIDANCE: dict[str, dict[str, Any]] = {
    "dev": {
        "goal": "Minimize idle hours; start resources only when needed.",
        "patterns": [
            "Use local containers for unit tests; deploy cloud dependencies on demand.",
            "Use scheduled start/stop or short-lived environments with TTL cleanup.",
            "Avoid NAT Gateway, load balancers, and always-on clusters unless the design needs them.",
            "Use short log retention only where security and audit policy permits.",
        ],
        "tradeoffs": ["Lower availability is usually acceptable only if documented.", "Do not use production data without approved protection."],
    },
    "test": {
        "goal": "Pay for test execution, not idle infrastructure.",
        "patterns": [
            "Use ephemeral CI runners and containers; cache dependencies and promote built artifacts.",
            "Use Spot only for retryable, interruptible workers.",
            "Create databases and test stacks per run and clean them up with a TTL.",
            "Avoid Kubernetes for small workloads unless Kubernetes behavior itself is under test.",
        ],
        "tradeoffs": ["Tests must tolerate ephemeral dependencies and retries.", "Keep representative integration tests."],
    },
    "staging": {
        "goal": "Preserve release-critical behavior while scaling nonessential capacity down.",
        "patterns": [
            "Match production runtime, networking, deployment, and migration paths where needed.",
            "Reduce instance size, replicas, retention, and schedules only where test objectives allow.",
            "Use production-like security controls and synthetic or sanitized data.",
            "Measure whether always-on NAT, load balancers, and replicas are actually required.",
        ],
        "tradeoffs": ["A single-AZ or reduced-replica setup does not validate production resilience."],
    },
    "production": {
        "goal": "Optimize cost per reliable transaction without violating SLOs.",
        "patterns": [
            "Right-size using representative CPU, memory, network, and application telemetry.",
            "Use Savings Plans/Reserved capacity only for stable baseline demand; use Spot for fault-tolerant tiers.",
            "Use autoscaling, storage lifecycle policies, and log retention aligned to compliance.",
            "Review NAT/data transfer paths, idle load balancers, unattached EBS, snapshots, public IPv4, and unused endpoints.",
        ],
        "tradeoffs": ["Do not remove redundancy, backups, security, or observability without risk and compliance approval."],
    },
}

def _monthly_total(architecture: dict[str, Any]) -> tuple[float, list[str]]:
    components = architecture.get("components") or {}
    total = 0.0
    unknown: list[str] = []
    for name in COST_COMPONENTS:
        value = components.get(name)
        if value is None:
            unknown.append(name)
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            unknown.append(name)
            continue
        if number < 0:
            raise ValueError(f"Monthly component cost cannot be negative: {name}")
        total += number
    for name, value in components.items():
        if name not in COST_COMPONENTS and value is not None:
            try:
                number = float(value)
            except (TypeError, ValueError):
                unknown.append(str(name))
                continue
            if number < 0:
                raise ValueError(f"Monthly component cost cannot be negative: {name}")
            total += number
    return round(total, 2), unknown

def compare_architectures(current: dict[str, Any], alternative: dict[str, Any]) -> dict[str, Any]:
    """Compare two user-entered monthly cost models with transparent unknowns."""
    current_total, current_unknown = _monthly_total(current)
    alternative_total, alternative_unknown = _monthly_total(alternative)
    delta = round(current_total - alternative_total, 2)
    known_current = len(current_unknown) == 0
    known_alternative = len(alternative_unknown) == 0
    return {
        "currency": current.get("currency", alternative.get("currency", "USD")),
        "current": {"name": current.get("name", "Current"), "monthly_total_of_entered_components": current_total,
                    "unknown_components": current_unknown, "complete": known_current},
        "alternative": {"name": alternative.get("name", "Alternative"), "monthly_total_of_entered_components": alternative_total,
                        "unknown_components": alternative_unknown, "complete": known_alternative},
        "estimated_monthly_difference": delta if known_current and known_alternative else None,
        "estimated_annual_difference": round(delta * 12, 2) if known_current and known_alternative else None,
        "direction": ("lower_cost" if delta > 0 else "higher_cost" if delta < 0 else "same_entered_cost") if known_current and known_alternative else "incomplete_inputs",
        "warning": "User-entered estimates only; not live AWS prices or guaranteed savings. Fill every component, validate region, usage, discounts, taxes, free-tier eligibility, and workload parity before deciding.",
    }

def audit_integration_gaps(inventory: dict[str, Any], billing_services: list[dict[str, Any]]) -> dict[str, Any]:
    """Identify coverage gaps between known inventory service families and billing rows."""
    discovered = {str(s).strip().lower() for s in inventory.get("discovered_service_families", [])}
    configured = {str(s).strip().lower() for s in inventory.get("integrated_service_families", [])}
    billed = {}
    for row in billing_services:
        service = str(row.get("service", "Unknown")).strip()
        try:
            amount = float(row.get("amount", 0) or 0)
        except (TypeError, ValueError):
            amount = None
        billed[service] = amount
    unintegrated_discovered = sorted(discovered - configured)
    billed_unmapped = sorted(
        [{"service": name, "amount": amount} for name, amount in billed.items()
         if name.strip().lower() not in configured],
        key=lambda row: row["service"].lower(),
    )
    return {
        "discovered_but_not_integrated": unintegrated_discovered,
        "billing_services_not_mapped_to_integrations": billed_unmapped,
        "note": "Billing service names and resource inventory do not map one-to-one. Treat these as investigation leads, not proof of waste or permission to delete resources.",
    }

def environment_blueprint(environment: str) -> dict[str, Any]:
    """Return the practical low-cost blueprint for a supported environment."""
    key = environment.strip().lower()
    if key not in ENVIRONMENT_GUIDANCE:
        raise ValueError(f"environment must be one of: {', '.join(ENVIRONMENT_GUIDANCE)}")
    return {"environment": key, **ENVIRONMENT_GUIDANCE[key]}
