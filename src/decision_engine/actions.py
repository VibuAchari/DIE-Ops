"""
src/decision_engine/actions.py

Enterprise Retention Action Space (ONE offer per customer)

Instead of "selecting customers", real systems assign interventions:

- EMAIL_NUDGE  (cheap digital)
- COUPON_10    (incentive)
- VIP_CALL     (high-touch)

Rules:
- Each customer generates multiple action candidates
- Optimizer later chooses the best ONE under budget
"""

from dataclasses import dataclass
from typing import Callable, List
import pandas as pd


# ------------------------------------------------------------
@dataclass
class OfferAction:
    name: str
    cost: float
    rule: Callable


# ------------------------------------------------------------
def get_offer_catalog() -> List[OfferAction]:
    """
    Defines realistic retention interventions.
    """

    return [

        # Cheap baseline action
        OfferAction(
            name="EMAIL_NUDGE",
            cost=5.0,
            rule=lambda r: r["churn_prob"] >= 0.15
        ),

        # Discount offer (only if uplift exists)
        OfferAction(
            name="COUPON_10",
            cost=50.0,
            rule=lambda r: (
                r["churn_prob"] >= 0.30 and
                r["uplift"] >= 0.03 and
                r["cltv_raw"] >= 3000
            )
        ),

        # High-touch only for valuable customers
        OfferAction(
            name="VIP_CALL",
            cost=200.0,
            rule=lambda r: (
                r["churn_prob"] >= 0.45 and
                r["uplift"] >= 0.05 and
                r["cltv_raw"] >= 40000
            )
        ),
    ]


# ------------------------------------------------------------
def build_action_candidates(df: pd.DataFrame, margin: float) -> pd.DataFrame:
    """
    Expand customers → action-level candidates.

    Output columns:
    - customer_id
    - offer
    - churn_prob
    - uplift
    - cltv
    - cost
    - expected_gain
    - net_profit
    """

    offers = get_offer_catalog()
    rows = []

    for _, r in df.iterrows():

        for offer in offers:

            # Apply eligibility rule
            if not offer.rule(r):
                continue

            # Expected value of intervention
            expected_gain = (
                r["churn_prob"] *
                r["uplift"] *
                r["cltv_raw"] *
                margin
            )

            net_profit = expected_gain - offer.cost

            # Skip non-profitable actions early
            if net_profit <= 0:
                continue

            rows.append({
                "customer_id": int(r["customer_id"]),
                "offer": offer.name,
                "churn_prob": float(r["churn_prob"]),
                "uplift": float(r["uplift"]),
                "cltv": float(r["cltv_raw"]),
                "cost": float(offer.cost),
                "expected_gain": float(expected_gain),
                "net_profit": float(net_profit)
            })

    return pd.DataFrame(rows)
