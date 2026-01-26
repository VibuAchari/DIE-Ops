"""
src/reporting/pdf_export.py

LOCKED Executive Campaign PDF Generator

Input:
- summary dict (from /recommend)
- customers list (selected_customers from /recommend)

Output:
- Enterprise-ready PDF report
"""

import matplotlib.pyplot as plt
from fpdf import FPDF
from collections import Counter


# ------------------------------------------------------------
# Chart Builders
# ------------------------------------------------------------

def chart_offer_mix(customers, path="offer_mix.png"):
    offers = [c["offer"] for c in customers]
    counts = Counter(offers)

    plt.figure()
    plt.bar(counts.keys(), counts.values())
    plt.title("Intervention Mix Deployed")
    plt.xlabel("Offer Type")
    plt.ylabel("Customers Targeted")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def chart_profit_distribution(customers, path="profit_distribution.png"):
    profits = [c["net_profit"] for c in customers]

    plt.figure()
    plt.hist(profits, bins=10)
    plt.title("Net Profit Distribution (Selected Customers)")
    plt.xlabel("Expected Net Profit (₹)")
    plt.ylabel("Customer Count")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def chart_roi_scatter(customers, path="roi_scatter.png"):
    costs = [c["cost"] for c in customers]
    profits = [c["net_profit"] for c in customers]

    plt.figure()
    plt.scatter(costs, profits)
    plt.title("Cost vs Expected Profit Efficiency")
    plt.xlabel("Intervention Cost (₹)")
    plt.ylabel("Expected Net Profit (₹)")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


# ------------------------------------------------------------
# Human Explanation Generator
# ------------------------------------------------------------

def explain_customer(c):
    churn = c["churn_prob"]
    uplift = c["uplift"]
    cltv = c["cltv_raw"]
    offer = c["offer"]

    reasons = []

    if churn >= 0.7:
        reasons.append("Customer shows high disengagement risk.")
    elif churn >= 0.4:
        reasons.append("Customer behavior indicates early churn movement.")
    else:
        reasons.append("Customer is stable but still benefits from retention.")

    if uplift >= 0.15:
        reasons.append("Intervention impact is expected to be strong.")
    elif uplift >= 0.05:
        reasons.append("Intervention impact is positive but moderate.")
    else:
        reasons.append("Intervention impact is limited; low-cost action preferred.")

    if cltv >= 50000:
        reasons.append("Customer has high lifetime value worth protecting.")
    elif cltv >= 10000:
        reasons.append("Customer value supports reasonable retention spending.")
    else:
        reasons.append("Customer value supports only lightweight action.")

    reasons.append(f"Recommended intervention: {offer}")

    return " ".join(reasons)


# ------------------------------------------------------------
# PDF Generator (LOCKED Style)
# ------------------------------------------------------------

def generate_campaign_pdf(summary, customers, output_file="campaign_report.pdf"):

    # --- Charts ---
    chart_offer_mix(customers)
    chart_profit_distribution(customers)
    chart_roi_scatter(customers)

    # --- PDF Setup ---
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "DIE-Ops Retention Campaign Report", ln=True, align="C")

    pdf.ln(8)

    # --------------------------------------------------------
    # Executive Summary
    # --------------------------------------------------------
    pdf.set_font("Helvetica", style="B", size=13)
    pdf.cell(0, 10, "1. Executive Outcome Summary", ln=True)

    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7,
        f"Customers Selected: {summary['selected_count']}\n"
        f"Total Budget Used: ₹{summary['budget_used']:,.0f}\n"
        f"Expected Total Net Profit: ₹{summary['expected_profit']:,.0f}\n"
        f"Average ROI per Customer: ₹{summary['avg_profit_per_customer']:,.0f}"
    )

    pdf.ln(6)

    # --------------------------------------------------------
    # Charts Section
    # --------------------------------------------------------
    pdf.set_font("Helvetica", style="B", size=13)
    pdf.cell(0, 10, "2. Campaign Intervention Analytics", ln=True)

    pdf.ln(4)
    pdf.image("offer_mix.png", w=170)
    pdf.ln(6)

    pdf.image("profit_distribution.png", w=170)
    pdf.ln(6)

    pdf.image("roi_scatter.png", w=170)
    pdf.ln(8)

    # --------------------------------------------------------
    # Customer-Level Explainability
    # --------------------------------------------------------
    pdf.set_font("Helvetica", style="B", size=13)
    pdf.cell(0, 10, "3. Customer-Level Decision Explanations", ln=True)

    pdf.set_font("Helvetica", size=10)

    top_customers = sorted(customers, key=lambda x: x["net_profit"], reverse=True)[:8]

    for c in top_customers:
        pdf.ln(4)
        pdf.set_font("Helvetica", style="B", size=10)
        pdf.cell(
            0,
            6,
            f"Customer {c['customer_id']} → {c['offer']} | Profit: ₹{c['net_profit']:,.0f}",
            ln=True
        )

        pdf.set_font("Helvetica", size=9)
        pdf.multi_cell(0, 5, explain_customer(c))

    # --------------------------------------------------------
    # Footer Close
    # --------------------------------------------------------
    pdf.ln(10)
    pdf.set_font("Helvetica", size=9)
    pdf.multi_cell(
        0,
        5,
        "This report is generated directly from the deployed decision engine output "
        "and reflects profit-positive retention interventions under the given budget."
    )

    # Save
    pdf.output(output_file)

    print(f"[report] PDF generated → {output_file}")