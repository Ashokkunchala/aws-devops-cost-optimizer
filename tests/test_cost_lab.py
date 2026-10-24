import pytest

from cost_optimizer.cost_lab import (
    audit_integration_gaps,
    compare_architectures,
    environment_blueprint,
)


def full(name, **overrides):
    components = {
        "compute": 100, "database": 50, "storage": 10, "load_balancing": 20,
        "nat_and_endpoints": 30, "data_transfer": 5, "logs_and_metrics": 10,
        "security": 5, "backup": 5, "dns": 1, "support": 0, "other": 0,
    }
    components.update(overrides)
    return {"name": name, "currency": "USD", "components": components}


def test_complete_architecture_comparison_calculates_delta():
    result = compare_architectures(full("current"), full("lean", compute=60, nat_and_endpoints=0))
    assert result["current"]["monthly_total_of_entered_components"] == 236
    assert result["alternative"]["monthly_total_of_entered_components"] == 166
    assert result["estimated_monthly_difference"] == 70
    assert result["estimated_annual_difference"] == 840
    assert result["direction"] == "lower_cost"
    assert "not live AWS prices" in result["warning"]


def test_missing_cost_components_prevent_savings_claim():
    result = compare_architectures(
        {"name": "current", "components": {"compute": 100}},
        {"name": "alternative", "components": {"compute": 50}},
    )
    assert result["estimated_monthly_difference"] is None
    assert result["direction"] == "incomplete_inputs"
    assert "database" in result["current"]["unknown_components"]


def test_negative_cost_rejected():
    with pytest.raises(ValueError):
        compare_architectures({"components": {"compute": -1}}, full("alternative"))


def test_billing_rows_not_integrated_are_reported_as_leads():
    result = audit_integration_gaps(
        {"discovered_service_families": ["EC2", "RDS"], "integrated_service_families": ["EC2"]},
        [{"service": "Amazon EC2", "amount": 12}, {"service": "Amazon RDS", "amount": 8}],
    )
    assert result["discovered_but_not_integrated"] == ["rds"]
    assert [row["service"] for row in result["billing_services_not_mapped_to_integrations"]] == [
        "Amazon EC2", "Amazon RDS"
    ]
    assert "not proof of waste" in result["note"]


@pytest.mark.parametrize("environment", ["dev", "test", "staging", "production"])
def test_all_environment_blueprints_have_tradeoffs(environment):
    result = environment_blueprint(environment)
    assert result["environment"] == environment
    assert result["patterns"]
    assert result["tradeoffs"]


def test_unknown_environment_rejected():
    with pytest.raises(ValueError):
        environment_blueprint("sandbox-unknown")
