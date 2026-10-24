"""Generate a self-contained, escaped HTML report."""

from __future__ import annotations

import html
import json
from typing import Any


def render_html(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    findings = report.get("findings", [])
    costs = report.get("cost_explorer")
    cards = [
        ("EC2 instances", summary.get("ec2_instances_scanned", 0)),
        ("EBS volumes", summary.get("ebs_volumes_scanned", 0)),
        ("Review findings", summary.get("findings", len(findings))),
    ]
    card_html = "".join(
        '<div class="card"><div class="muted">'
        + html.escape(str(label))
        + '</div><div class="number">'
        + html.escape(str(value))
        + "</div></div>"
        for label, value in cards
    )
    rows = []
    for finding in findings:
        evidence = json.dumps(finding.get("evidence", {}), ensure_ascii=False, sort_keys=True)
        rows.append(
            "<tr>"
            + "".join(
                "<td>" + html.escape(str(value if value is not None else "")) + "</td>"
                for value in (
                    finding.get("severity"),
                    finding.get("resource_type"),
                    finding.get("resource_id"),
                    finding.get("finding"),
                    evidence,
                    finding.get("recommendation"),
                )
            )
            + "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="6">No findings in this report.</td></tr>')

    cost_section = '<p class="muted">Cost Explorer data was not requested.</p>'
    if costs:
        amount = costs.get("total_actual_cost", 0)
        currency = costs.get("currency", "")
        service_rows = "".join(
            "<tr><td>" + html.escape(str(item.get("service", ""))) + "</td><td>"
            + html.escape(str(item.get("amount", 0))) + " "
            + html.escape(str(item.get("currency", currency))) + "</td></tr>"
            for item in costs.get("by_service", [])
        )
        cost_section = (
            '<div class="cost-total">Actual unblended cost: '
            + html.escape(str(amount)) + " " + html.escape(str(currency)) + "</div>"
            + "<p class=\"muted\">Period: "
            + html.escape(str(costs.get("start_date", ""))) + " to (exclusive) "
            + html.escape(str(costs.get("end_date_exclusive", ""))) + ". "
            + html.escape(str(costs.get("note", ""))) + "</p>"
            + "<table><thead><tr><th>Service</th><th>Actual cost</th></tr></thead><tbody>"
            + (service_rows or '<tr><td colspan="2">No service cost rows returned.</td></tr>')
            + "</tbody></table>"
        )

    generated = html.escape(str(report.get("generated_at", "")))
    region = html.escape(str(report.get("region") or "not specified"))
    mode = html.escape(str(report.get("mode", "unknown")))
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AWS DevOps Cost Optimizer Report</title>
<style>
:root{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#172033;background:#f5f7fb}
body{margin:0;padding:28px;max-width:1400px;margin-inline:auto}
h1,h2{line-height:1.2}.muted{color:#5d6678;font-size:.92rem}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}
.card,section{background:white;border:1px solid #e1e6ef;border-radius:12px;padding:16px;margin:14px 0}
.number{font-size:1.8rem;font-weight:700}.cost-total{font-size:1.35rem;font-weight:700;margin-top:12px}
.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;background:white}
th,td{text-align:left;vertical-align:top;padding:10px;border-bottom:1px solid #e5e9f0;overflow-wrap:anywhere}
th{background:#edf1f7}td{font-size:.9rem}.notice{border-left:4px solid #64748b;padding:10px 14px;background:#eef2f7}
@media(max-width:600px){body{padding:12px}}
</style></head><body>
<h1>AWS DevOps Cost Optimizer</h1>
<p class="muted">Generated: """ + generated + """ · Region: """ + region + """ · Mode: """ + mode + """</p>
<div class="notice">Read-only report. Findings are review candidates, not authorization to change or delete resources. Savings are not inferred from inventory alone.</div>
<div class="cards">""" + card_html + """</div>
<section><h2>Billing summary</h2>""" + cost_section + """</section>
<section><h2>Optimization findings</h2><div class="table-wrap"><table>
<thead><tr><th>Severity</th><th>Resource type</th><th>Resource ID</th><th>Finding</th><th>Evidence</th><th>Recommended review</th></tr></thead>
<tbody>""" + "".join(rows) + """</tbody></table></div></section>
<p class="muted">Mutations performed: no. Human review required: yes.</p>
</body></html>
"""
