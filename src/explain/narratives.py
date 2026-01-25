"""
src/explain/narratives.py

Enterprise Explainability Layer (Human-Readable Decision Narratives)

Purpose:
- Convert churn + uplift + CLTV economics into business-facing explanations
- Designed for marketing and retention teams, not data scientists

This is NOT feature attribution.
This is decision justification:
    "High churn risk + strong uplift + valuable customer = action worth funding"

Outputs:
- Customer-level bullet narratives
- Campaign-level executive summaries
"""

from typing import Dict, List


# ------------------------------------------------------------
def explain_customer(row: Dict) -> Dict:
    """
    Generate a human-readable explanation for ONE customer decision.

    Expected input fields:
    - customer_id
    - churn_prob
    - uplift
    - cltv
    - offer
    - net_profit
    """

    churn = float(row["churn_prob"])
    uplift = float(row["uplift"])
    cltv = float(row["cltv"])
    offer = row["offer"]
    profit = float(row["net_profit"])

    reasons: List[str] = []

    # --------------------------------------------------------
    # 1. Churn Risk Narrative
    # --------------------------------------------------------
    if churn >= 0.70:
        reasons.append(
            "Very high churn risk: this customer is likely to leave soon without intervention."
        )
    elif churn >= 0.40:
        reasons.append(
            "Moderate churn risk: engagement is declining and retention action is justified."
        )
    else:
        reasons.append(
            "Lower churn risk: customer is still active, but proactive retention may help."
        )

    # --------------------------------------------------------
    # 2. Uplift Narrative (Treatment Impact)
    # --------------------------------------------------------
    if uplift < 0:
        reasons.append(
            "Negative uplift detected: retention treatment may backfire, so targeting is risky."
        )
    elif uplift >= 0.20:
        reasons.append(
            "Strong uplift: retention action is expected to significantly reduce churn."
        )
    elif uplift >= 0.05:
        reasons.append(
            "Positive uplift: customer should respond well to retention treatment."
        )
    else:
        reasons.append(
            "Weak uplift: expected retention impact is limited."
        )

    # --------------------------------------------------------
    # 3. Customer Value Narrative (CLTV)
    # --------------------------------------------------------
    if cltv >= 50000:
        reasons.append(
            "High-value customer: premium retention investment is economically worthwhile."
        )
    elif cltv >= 10000:
        reasons.append(
            "Mid-value customer: retention spending is reasonable given expected returns."
        )
    else:
        reasons.append(
            "Low-value customer: only low-cost interventions make business sense."
        )

    # --------------------------------------------------------
    # 4. Offer Justification (Action Assignment)
    # --------------------------------------------------------
    if offer == "EMAIL_NUDGE":
        reasons.append(
            "Selected EMAIL_NUDGE because it is a low-cost digital intervention with positive ROI."
        )

    elif offer == "COUPON_10":
        reasons.append(
            "Selected COUPON_10 because churn risk is high and a financial incentive improves retention."
        )

    elif offer == "VIP_CALL":
        reasons.append(
            "Selected VIP_CALL because the customer is highly valuable and human outreach is justified."
        )

    else:
        reasons.append(
            f"Recommended action: {offer} (best available profit-positive intervention)."
        )

    # --------------------------------------------------------
    # 5. ROI Outcome
    # --------------------------------------------------------
    reasons.append(
        f"Expected net profit from this action: ₹{profit:,.0f}"
    )

    return {
        "customer_id": int(row["customer_id"]),
        "offer": offer,
        "reasons": reasons
    }


# ------------------------------------------------------------
def explain_campaign(selected_customers: List[Dict]) -> Dict:
    """
    Generate an executive-friendly campaign summary.

    Output:
    - Campaign-level bullets
    - Offer distribution
    """

    if not selected_customers:
        return {
            "campaign_summary": [
                "No profitable retention actions were found under the given budget."
            ]
        }

    total = len(selected_customers)

    # Count actions
    offer_counts = {}
    total_profit = 0.0

    for c in selected_customers:
        offer_counts[c["offer"]] = offer_counts.get(c["offer"], 0) + 1
        total_profit += float(c["net_profit"])

    # Executive bullets
    bullets = [
        f"Campaign selected {total} customers with positive expected ROI.",
        "Actions were assigned based on churn risk, expected uplift impact, and customer value.",
        f"Expected total net profit: ₹{total_profit:,.0f}",
    ]

    # Offer breakdown
    bullets.append("Offer mix deployed:")

    for offer, n in offer_counts.items():
        bullets.append(f"- {offer}: {n} customers")

    return {"campaign_summary": bullets}