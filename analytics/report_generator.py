# src/analytics/report_generator.py
"""
Simple campaign strategy HTML report generator.

Inputs:
 - summary: dict returned by optimizer
 - selected_df: DataFrame returned by optimizer
 - campaign_meta: dict (name, budget, cost_per_action, margin, created_by)

Produces:
 - HTML report written to out_path (openable in browser)
"""
import pandas as pd
import datetime
import os
from typing import Dict

HTML_TEMPLATE = """
<html>
<head><title>Campaign Strategy Report - {campaign_name}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 30px; }}
h1 {{ color: #114b8a; }}
.kv {{ display:flex; gap:20px; }}
.kv div {{ background:#f3f6fb; padding:10px; border-radius:6px; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
th, td {{ border: 1px solid #ddd; padding: 8px; }}
th {{ background: #114b8a; color: white; }}
</style>
</head>
<body>
<h1>Campaign Strategy Report — {campaign_name}</h1>
<p>Generated: {ts}</p>

<div class="kv">
  <div><strong>Budget</strong><br/>{budget}</div>
  <div><strong>Selected Count</strong><br/>{selected_count}</div>
  <div><strong>Spent</strong><br/>{spent:.2f}</div>
  <div><strong>Expected Incremental Gain</strong><br/>{expected_total_gain:.2f}</div>
  <div><strong>Avg ROI</strong><br/>{avg_roi:.2f}</div>
</div>

<h2>Top 25 Selected Customers</h2>
{table}

<h2>Executive Summary</h2>
<p>
This campaign targets <strong>{selected_count}</strong> customers selected by ROI priority. The
expected incremental gain is <strong>{expected_total_gain:.2f}</strong> on a spend of <strong>{spent:.2f}</strong>,
yielding an average ROI of <strong>{avg_roi:.2f}</strong>.
</p>

<h3>Actionable Recommendations</h3>
<ul>
<li>Run a small pilot (1k customers) to validate uplift estimates before scaling.</li>
<li>Focus on high-ROI segments and avoid blanket discounts to low-CLTV customers.</li>
<li>Instrument A/B testing to validate predicted uplift and recalibrate the models.</li>
</ul>

</body>
</html>
"""

def generate_campaign_report(selected_df: pd.DataFrame, summary: Dict, campaign_meta: Dict, out_path: str):
    selected_count = summary.get("selected_count", 0)
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    table_html = ""
    if selected_count > 0:
        top = selected_df.head(25)[["customer_id", "uplift", "cltv", "cost", "expected_gain", "roi"]]
        table_html = top.to_html(index=False, float_format="%.4f")
    html = HTML_TEMPLATE.format(
        campaign_name=campaign_meta.get("name", "Campaign"),
        ts=ts,
        budget=campaign_meta.get("budget", 0.0),
        selected_count=selected_count,
        spent=summary.get("spent", 0.0),
        expected_total_gain=summary.get("expected_total_gain", 0.0),
        avg_roi=summary.get("avg_roi", 0.0),
        table=table_html
    )
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
