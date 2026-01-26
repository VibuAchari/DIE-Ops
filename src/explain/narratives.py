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
    Generate a business-readable explanation for ONE customer decision.

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
            "Customer shows strong churn signals and is likely to disengage soon without intervention."
        )
    elif churn >= 0.40:
        reasons.append(
            "Customer engagement is weakening, making early retention action economically justified."
        )
    else:
        reasons.append(
            "Customer is still active, but proactive retention helps prevent gradual drop-off."
        )

    # --------------------------------------------------------
    # 2. Treatment Impact Narrative (Uplift)
    # --------------------------------------------------------
    if uplift < 0:
        reasons.append(
            "Predicted response is negative: retention targeting is risky and may reduce engagement."
        )
    elif uplift >= 0.20:
        reasons.append(
            "Strong expected response: intervention is likely to significantly reduce churn probability."
        )
    elif uplift >= 0.05:
        reasons.append(
            "Positive expected response: customer should benefit from targeted retention treatment."
        )
    else:
        reasons.append(
            "Limited expected response: retention impact is modest but still positive compared to inaction."
        )

    # --------------------------------------------------------
    # 3. Customer Value Narrative (CLTV)
    # --------------------------------------------------------
    if cltv >= 50000:
        reasons.append(
            "High lifetime value customer: retention investment is financially important."
        )
    elif cltv >= 10000:
        reasons.append(
            "Mid-value customer: retention spend is reasonable if ROI remains positive."
        )
    else:
        reasons.append(
            "Lower-value customer: only cost-efficient actions are economically viable."
        )

    # --------------------------------------------------------
    # 4. Policy-Based Offer Justification (Not Hardcoded)
    # --------------------------------------------------------
    reasons.append(
        f"Recommended action: {offer}, selected because it produced the highest expected profit "
        "among available retention interventions for this customer."
    )

    # --------------------------------------------------------
    # 5. ROI Outcome
    # --------------------------------------------------------
    reasons.append(
        f"Expected net profit impact after intervention cost: ₹{profit:,.0f}"
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
    - Profitability framing
    """

    if not selected_customers:
        return {
            "campaign_summary": [
                "No retention interventions were profitable under the given budget constraints."
            ]
        }

    total = len(selected_customers)

    # Count actions + profit
    offer_counts = {}
    total_profit = 0.0

    for c in selected_customers:
        offer_counts[c["offer"]] = offer_counts.get(c["offer"], 0) + 1
        total_profit += float(c["net_profit"])

    # Executive bullets
    bullets = [
        f"Campaign prioritized {total} customers with the strongest profit-positive churn risk.",
        "Interventions were personalized using churn urgency, expected uplift, and customer lifetime value.",
        f"Expected total incremental net profit: ₹{total_profit:,.0f}",
        "Intervention mix deployed:"
    ]

    # Offer breakdown
    for offer, n in sorted(offer_counts.items(), key=lambda x: -x[1]):
        bullets.append(f"- {offer}: {n} customers")

    return {"campaign_summary": bullets}
