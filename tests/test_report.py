from cost_optimizer.report import build_report


def test_report_does_not_invent_savings():
    report = build_report({"mode": "local_fixture", "ec2_instances": [{}], "ebs_volumes": []}, [])
    assert report["summary"]["ec2_instances_scanned"] == 1
    assert report["summary"]["estimated_monthly_savings"] is None
    assert report["safety"]["mutations_performed"] is False
    assert report["safety"]["human_review_required"] is True
