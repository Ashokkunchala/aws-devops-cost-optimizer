"""Render a self-contained neon FinOps dashboard from the optimizer report."""

from __future__ import annotations

import html
import json
from typing import Any


def _e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""))


def _money(value: Any, currency: str = "") -> str:
    try:
        number = float(value)
        rendered = f"{number:,.2f}"
    except (TypeError, ValueError):
        rendered = str(value if value is not None else "—")
    return f"{_e(currency)} {_e(rendered)}".strip()


def render_html(report: dict[str, Any]) -> str:
    summary = report.get("summary") or {}
    findings = report.get("findings") or []
    costs = report.get("cost_explorer") or {}
    currency = str(costs.get("currency") or "")
    by_service = costs.get("by_service") or []
    total_cost = costs.get("total_actual_cost")
    instances = summary.get("ec2_instances_scanned", 0)
    volumes = summary.get("ebs_volumes_scanned", 0)
    finding_count = summary.get("findings", len(findings))
    generated = _e(report.get("generated_at", ""))
    region = _e(report.get("region") or "not specified")
    mode = _e(report.get("mode", "unknown"))
    period = ""
    if costs:
        period = f"{_e(costs.get('start_date', ''))} → {_e(costs.get('end_date_exclusive', ''))} (end exclusive)"

    service_total = 0.0
    for item in by_service:
        try:
            service_total += float(item.get("amount", 0) or 0)
        except (TypeError, ValueError):
            pass
    max_service = max(
        [float(item.get("amount", 0) or 0) for item in by_service if str(item.get("amount", "")).replace(".", "", 1).replace("-", "", 1).isdigit()]
        or [1.0]
    )
    service_colors = ["#18c8f3", "#12d6b0", "#8a7dff", "#f4a340", "#e36dca", "#6d9dff"]
    service_rows = []
    service_bars = []
    for index, item in enumerate(sorted(by_service, key=lambda row: float(row.get("amount", 0) or 0), reverse=True)):
        name = _e(item.get("service", "Unknown service"))
        amount = item.get("amount", 0)
        item_currency = str(item.get("currency") or currency)
        color = service_colors[index % len(service_colors)]
        try:
            pct = max(0, min(100, float(amount) / max_service * 100))
        except (TypeError, ValueError, ZeroDivisionError):
            pct = 0
        service_rows.append(
            f'<div class="service-row"><div class="service-label"><span class="dot" style="--dot:{color}"></span>'
            f'<span>{name}</span><b>{_money(amount, item_currency)}</b></div>'
            f'<div class="track"><span style="width:{pct:.2f}%;--bar:{color}"></span></div></div>'
        )
        service_bars.append(
            f'<div class="mini-bar" title="{name}: {_money(amount, item_currency)}" style="height:{max(5, pct):.2f}%;--bar:{color}"></div>'
        )
    if not service_rows:
        service_rows_html = '<div class="empty">Enable Cost Explorer to show actual service-level spend.</div>'
        bars_html = '<div class="empty chart-empty">No billing series available yet</div>'
    else:
        service_rows_html = "".join(service_rows)
        bars_html = "".join(service_bars)

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    finding_rows = []
    for finding in findings:
        severity = str(finding.get("severity", "info")).lower()
        severity_counts[severity if severity in severity_counts else "info"] += 1
        evidence = json.dumps(finding.get("evidence", {}), ensure_ascii=False, sort_keys=True)
        resource = finding.get("resource_id", "—")
        finding_rows.append(
            "<tr>"
            f'<td><span class="severity sev-{_e(severity)}">{_e(severity)}</span></td>'
            f'<td>{_e(finding.get("resource_type", "—"))}</td>'
            f'<td class="mono">{_e(resource)}</td>'
            f'<td><strong>{_e(finding.get("finding", "—"))}</strong>'
            f'<small>{_e(finding.get("recommendation", ""))}</small></td>'
            f'<td><code>{_e(evidence)}</code></td></tr>'
        )
    if not finding_rows:
        finding_rows.append('<tr><td colspan="5" class="empty">No findings were returned by this scan.</td></tr>')

    cost_display = _money(total_cost, currency) if costs else "Not connected"
    monthly_savings = summary.get("estimated_monthly_savings")
    savings_display = _money(monthly_savings, currency) if monthly_savings is not None else "Not calculated"
    cost_note = _e(costs.get("note", "Actual unblended costs reported by Cost Explorer; not a savings estimate.")) if costs else "Run with --cost-explorer to load actual billing data."
    cost_period = f'<div class="period">{period}</div>' if period else ""
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><title>AWS Cost Explorer · DevOps FinOps</title>
<style>
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;color:#d9efff;background:#030916;font-synthesis:none}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 50% -20%,#0c2b4a 0,#050d1b 42%,#020611 100%);min-height:100vh;padding:18px}
.shell{max-width:1800px;margin:auto;border:1px solid #15334b;background:linear-gradient(145deg,rgba(5,17,33,.98),rgba(2,8,19,.98));box-shadow:0 0 40px #00b7ff12;overflow:hidden}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:18px 22px;border-bottom:1px solid #153d59;background:#061322}
.brand{display:flex;align-items:center;gap:12px;letter-spacing:.16em;font-weight:800;color:#70e4ff}.brand-icon{width:42px;height:42px;display:grid;place-items:center;border:1px solid #21c6ed;color:#20d9ff;transform:rotate(45deg);box-shadow:0 0 18px #00bfff26}.brand-icon span{transform:rotate(-45deg);font-size:21px}
.topmeta{font-size:11px;color:#7094ad;text-align:right;line-height:1.8}.live{color:#55edc0}.layout{display:grid;grid-template-columns:220px minmax(0,1fr) 260px;gap:12px;padding:14px}
.panel{border:1px solid #17405a;background:linear-gradient(145deg,rgba(8,27,46,.95),rgba(4,15,29,.96));position:relative;min-width:0;box-shadow:inset 0 0 22px #0b92c008}
.panel:before{content:"";position:absolute;left:0;top:0;width:40px;height:2px;background:#25d9ff;box-shadow:0 0 9px #25d9ff}
.panel-head{padding:14px 15px 10px;display:flex;justify-content:space-between;align-items:center;gap:8px;color:#76ddff;font-size:11px;font-weight:800;letter-spacing:.09em;text-transform:uppercase}
.panel-body{padding:0 15px 15px}.muted{color:#7393aa;font-size:11px}.tiny{font-size:10px;color:#6b91aa}.leftcol,.rightcol,.centercol{display:flex;flex-direction:column;gap:12px}
.filter-label{display:block;color:#7e9eb6;font-size:10px;margin:12px 0 5px}.fake-select{border:1px solid #1b4965;background:#071525;padding:9px;color:#c8e6f7;font-size:11px;display:flex;justify-content:space-between;gap:8px}.chip{display:inline-block;border:1px solid #215b77;padding:5px 7px;color:#82dfff;font-size:10px;margin:3px 2px 0 0}
.primary-btn{width:100%;border:1px solid #15bfe9;color:#5ee3ff;background:#09273a;padding:10px;margin-top:14px;font-weight:800;font-size:11px;letter-spacing:.05em}
.saved{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #153249;color:#b4d1e4;font-size:11px}.saved:last-child{border:0}
h1{font-size:clamp(20px,2.2vw,32px);letter-spacing:.17em;text-align:center;color:#76e6ff;margin:0;padding:8px 0 17px;text-shadow:0 0 18px #1bbff64a}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px}.kpi{padding:14px 13px;border:1px solid #19415b;background:#061629;min-width:0}.kpi-label{font-size:10px;color:#8caec4;text-transform:uppercase;letter-spacing:.07em}.kpi-value{font-size:clamp(18px,2vw,27px);font-weight:800;color:#e2f7ff;margin:9px 0 5px;overflow-wrap:anywhere}.kpi-foot{font-size:10px;color:#39d8b4}.kpi-foot.warn{color:#f6b95b}
.twocol{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:12px}.chart-wrap{padding:0 15px 15px}.chart-summary{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:14px}.chart-summary strong{font-size:17px}.legend{display:flex;flex-wrap:wrap;gap:10px;margin-top:13px}.legend span{font-size:10px;color:#8da9bd}.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--dot);margin-right:7px;box-shadow:0 0 8px var(--dot)}
.bar-chart{height:160px;display:flex;align-items:flex-end;gap:7px;border-bottom:1px solid #28506a;border-left:1px solid #28506a;padding:10px 10px 0;background:repeating-linear-gradient(to top,transparent 0,transparent 38px,#143047 39px,#143047 40px);overflow:hidden}
.mini-bar{flex:1;min-width:5px;border:1px solid var(--bar);background:linear-gradient(to top,color-mix(in srgb,var(--bar) 32%,transparent),var(--bar));box-shadow:0 0 10px color-mix(in srgb,var(--bar) 22%,transparent);border-radius:2px 2px 0 0}
.empty{padding:18px;color:#7593a9;font-size:11px;text-align:center;border:1px dashed #24455b}.chart-empty{width:100%;align-self:center}.service-row{margin:13px 0}.service-label{display:flex;align-items:center;gap:4px;font-size:11px;color:#b8d6e8;margin-bottom:7px}.service-label span:nth-child(2){flex:1;overflow-wrap:anywhere}.service-label b{font-size:10px;color:#d7f4ff;white-space:nowrap}.track{height:5px;background:#102b40;overflow:hidden}.track span{height:100%;display:block;background:var(--bar);background:linear-gradient(90deg,var(--bar),#4fe5ff);box-shadow:0 0 10px var(--bar)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.stat{padding:10px;background:#071727;border:1px solid #17394f}.stat strong{display:block;font-size:19px;color:#73e6ff}.stat span{font-size:9px;color:#7e9cb1}
.alert{display:flex;gap:10px;padding:12px 0;border-bottom:1px solid #18374d}.alert:last-child{border:0}.alert-icon{font-size:17px}.alert strong{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.05em}.alert p{font-size:10px;line-height:1.5;color:#9ab5c7;margin:5px 0 0}.sev-critical,.sev-high{color:#ff7e8a}.sev-medium{color:#ffc46e}.sev-low{color:#71d9ff}.sev-info{color:#7fdcc4}.severity{font-size:10px;font-weight:800;text-transform:uppercase}.budget-row{margin:15px 0}.budget-label{display:flex;justify-content:space-between;gap:8px;font-size:10px;color:#c3d9e8}.budget-track{height:7px;background:#112d41;margin-top:8px}.budget-track span{display:block;height:100%;background:linear-gradient(90deg,#0ba8d9,#23e1d0)}.footnote{border-top:1px solid #17364b;padding:12px 16px;color:#688aa2;font-size:10px;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap}
.table-wrap{overflow:auto}.findings{width:100%;border-collapse:collapse;font-size:11px}.findings th{text-align:left;color:#7fdcff;background:#081b2e;font-size:9px;text-transform:uppercase;letter-spacing:.06em}.findings th,.findings td{padding:11px 12px;border-bottom:1px solid #16364c;vertical-align:top}.findings td{color:#b8d1e1}.findings small{display:block;color:#7899af;line-height:1.5;margin-top:5px}.findings code{font-size:10px;white-space:normal;overflow-wrap:anywhere;color:#89acc2}.mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
@media(max-width:1250px){.layout{grid-template-columns:190px minmax(0,1fr)}.rightcol{grid-column:1/-1;display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:780px){body{padding:0}.layout{grid-template-columns:1fr;padding:9px}.leftcol{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}.centercol{grid-row:1}.rightcol{grid-column:auto;grid-template-columns:1fr}.twocol{grid-template-columns:1fr}.topbar{padding:12px}.topmeta{font-size:9px}}
@media(max-width:460px){.leftcol{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.kpi{padding:11px}.kpi-value{font-size:18px}.brand{font-size:11px}.findings{min-width:680px}}
</style></head><body><div class="shell">
<header class="topbar"><div class="brand"><div class="brand-icon"><span>⌁</span></div><div>AWS FINOPS<br><span style="font-size:10px;color:#7b9fb7;letter-spacing:.24em">COST INTELLIGENCE</span></div></div>
<div class="topmeta"><span class="live">● READ-ONLY SCAN</span><br>REGION: """ + region + """ · MODE: """ + mode + """<br>GENERATED: """ + generated + """</div></header>
<div class="layout">
<aside class="leftcol">
<section class="panel"><div class="panel-head">Dimensions <span>⌃</span></div><div class="panel-body"><span class="filter-label">GROUP BY</span><div class="fake-select">Primary · Account <span>⌄</span></div><div class="fake-select" style="margin-top:6px">Secondary · Environment <span>⌄</span></div><span class="filter-label">ACTIVE SCAN</span><div class="chip">Region: """ + region + """</div><div class="chip">Read-only</div><div class="chip">Human review</div><div class="tiny" style="margin-top:14px">This report is a snapshot. Interactive AWS filters are not applied by this static HTML file.</div></div></section>
<section class="panel"><div class="panel-head">Saved views</div><div class="panel-body"><div class="saved">◉ Executive overview <span>☆</span></div><div class="saved">▦ Resource findings <span>☆</span></div><div class="saved">▤ Billing breakdown <span>☆</span></div><div class="saved">⌁ Security & safety <span>☆</span></div></div></section>
</aside>
<main class="centercol"><h1>COST EXPLORER</h1>
<div class="kpis">
<div class="kpi"><div class="kpi-label">Actual cost</div><div class="kpi-value">""" + cost_display + """</div><div class="kpi-foot">""" + ("Cost Explorer data" if costs else "Billing not requested") + """</div></div>
<div class="kpi"><div class="kpi-label">EC2 instances scanned</div><div class="kpi-value">""" + _e(instances) + """</div><div class="kpi-foot">Inventory count</div></div>
<div class="kpi"><div class="kpi-label">EBS volumes scanned</div><div class="kpi-value">""" + _e(volumes) + """</div><div class="kpi-foot">Attached and unattached</div></div>
<div class="kpi"><div class="kpi-label">Est. monthly savings</div><div class="kpi-value">""" + savings_display + """</div><div class="kpi-foot warn">Not inferred from inventory</div></div>
</div>
<div class="panel"><div class="panel-head">Cost & usage overview <span class="tiny">ACTUAL SERVICE COSTS</span></div><div class="chart-wrap"><div class="chart-summary"><div><div class="muted">Actual unblended cost</div><strong>""" + cost_display + """</strong><div class="tiny">""" + cost_note + """</div></div><div class="tiny">""" + period + """</div></div><div class="bar-chart" role="img" aria-label="Relative actual cost by service">""" + bars_html + """</div><div class="legend"><span><i class="dot" style="--dot:#18c8f3"></i>Bars show relative service spend</span><span>Forecast and usage series are not available in this report</span></div></div></div>
<div class="twocol">
<section class="panel"><div class="panel-head">Breakdown by service <span class="tiny">COST EXPLORER</span></div><div class="panel-body">""" + service_rows_html + """</div></section>
<section class="panel"><div class="panel-head">Optimization signals <span class="tiny">REVIEW REQUIRED</span></div><div class="panel-body"><div class="stats"><div class="stat"><strong>""" + _e(finding_count) + """</strong><span>FINDINGS</span></div><div class="stat"><strong>""" + _e(severity_counts["critical"] + severity_counts["high"]) + """</strong><span>HIGH / CRITICAL</span></div><div class="stat"><strong>""" + _e(len(findings)) + """</strong><span>REVIEW ITEMS</span></div></div><div class="alert"><span class="alert-icon">◇</span><div><strong class="sev-info">No auto-remediation</strong><p>The optimizer never stops, resizes, detaches, or deletes AWS resources.</p></div></div><div class="alert"><span class="alert-icon">ⓘ</span><div><strong class="sev-medium">Savings are not estimated</strong><p>Validated region-specific prices and workload evidence are required before savings can be calculated.</p></div></div></div></section>
</div>
<section class="panel"><div class="panel-head">Resource findings <span class="tiny">""" + _e(len(findings)) + """ ITEMS</span></div><div class="table-wrap"><table class="findings"><thead><tr><th>Severity</th><th>Resource</th><th>Resource ID</th><th>Finding & recommendation</th><th>Evidence</th></tr></thead><tbody>""" + "".join(finding_rows) + """</tbody></table></div></section>
</main>
<aside class="rightcol">
<section class="panel"><div class="panel-head">Budgets <span class="tiny">NOT CONFIGURED</span></div><div class="panel-body"><div class="empty">No budget limits were included in this scan.<br><br>Configure an AWS Budget separately to track actual usage against a limit.</div></div></section>
<section class="panel"><div class="panel-head">Alerts <span class="tiny">FINDINGS SUMMARY</span></div><div class="panel-body">
<div class="alert"><span class="alert-icon">""" + ("🔴" if severity_counts["critical"] else "🟠") + """</span><div><strong class="sev-critical">Critical</strong><p>""" + _e(severity_counts["critical"]) + """ critical findings in this report.</p></div></div>
<div class="alert"><span class="alert-icon">🟠</span><div><strong class="sev-high">High</strong><p>""" + _e(severity_counts["high"]) + """ high-severity findings require review.</p></div></div>
<div class="alert"><span class="alert-icon">🔹</span><div><strong class="sev-info">Inventory coverage</strong><p>Scanned """ + _e(instances) + """ EC2 instances and """ + _e(volumes) + """ EBS volumes.</p></div></div>
</div></section>
<section class="panel"><div class="panel-head">Recent insights</div><div class="panel-body"><div class="alert"><span class="alert-icon">▣</span><div><strong class="sev-info">Billing</strong><p>""" + ("Actual cost data is included." if costs else "Run with --cost-explorer to load actual cost data.") + """</p></div></div><div class="alert"><span class="alert-icon">⌁</span><div><strong class="sev-info">Resource review</strong><p>Use the findings table to inspect each recommendation before taking action.</p></div></div><div class="alert"><span class="alert-icon">✓</span><div><strong class="sev-info">Safety status</strong><p>Mutations performed: no. Human review required: yes.</p></div></div></div></section>
</aside>
</div><footer class="footnote"><span>DATA AS OF: """ + generated + """ · REGION: """ + region + """</span><span>Mutations performed: no · Human review required: yes · Review before action</span></footer></div></body></html>
"""
