from cost_optimizer.rules import analyze_inventory


def test_stopped_instance_is_review_only():
    findings = analyze_inventory({"ec2_instances": [{"instance_id": "i-1", "state": "stopped", "tags": {}}]})
    assert len(findings) == 1
    assert findings[0]["resource_id"] == "i-1"
    assert findings[0]["estimate_status"] == "not_calculated"
    assert "Confirm" in findings[0]["recommendation"]


def test_running_instance_missing_owner_tag():
    findings = analyze_inventory({"ec2_instances": [{"instance_id": "i-2", "state": "running", "tags": {}}]})
    assert len(findings) == 1
    assert findings[0]["finding"] == "Running instance missing an Owner tag"


def test_unattached_volume_is_not_deleted():
    findings = analyze_inventory({"ebs_volumes": [{"volume_id": "vol-1", "state": "available", "size_gib": 20}]})
    assert len(findings) == 1
    assert findings[0]["resource_type"] == "ebs_volume"
    assert "before considering removal" in findings[0]["recommendation"].lower()


def test_owned_instance_and_attached_volume_are_ignored():
    findings = analyze_inventory({
        "ec2_instances": [{"instance_id": "i-3", "state": "running", "tags": {"Owner": "team"}}],
        "ebs_volumes": [{"volume_id": "vol-2", "state": "in-use", "size_gib": 30}],
    })
    assert findings == []
