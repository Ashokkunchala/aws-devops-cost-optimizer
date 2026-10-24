from cost_optimizer.dashboard import render_html


def test_dashboard_escapes_untrusted_inventory_values():
    report = {
        "generated_at": "2026-01-01T00:00:00+00:00",
        "region": "ap-south-1",
        "mode": "fixture",
        "summary": {"ec2_instances_scanned": 1, "ebs_volumes_scanned": 0, "findings": 1},
        "findings": [{
            "severity": "low",
            "resource_type": "ec2_instance",
            "resource_id": "<script>alert(1)</script>",
            "finding": "Tag issue",
            "evidence": {"tag": "<b>bad</b>"},
            "recommendation": "Review & tag",
        }],
    }
    html = render_html(report)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "Mutations performed: no" in html


def test_dashboard_includes_cost_explorer_data_when_present():
    report = {
        "summary": {},
        "findings": [],
        "cost_explorer": {
            "total_actual_cost": 12.34,
            "currency": "USD",
            "start_date": "2026-01-01",
            "end_date_exclusive": "2026-02-01",
            "by_service": [{"service": "Amazon EC2", "amount": 12.34, "currency": "USD"}],
            "note": "actual cost only",
        },
    }
    html = render_html(report)
    assert "12.34" in html
    assert "Amazon EC2" in html
