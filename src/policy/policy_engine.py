"""
src/policy/policy_engine.py

Enterprise Policy Engine (Simulator-Based Intervention Assignment)

This is NOT a trained RL policy.
This is a simulator-driven decision policy that:

- evaluates multiple actions per customer
- estimates uplift based on action + customer type
- selects the profit-maximizing intervention
- supports scalable catalogs

Use-case:
Portfolio-grade intervention logic without historical treatment logs.
"""

from typing import Dict, List
import random


# ------------------------------------------------------------
# Scalable Action Catalog
# ------------------------------------------------------------
ACTIONS = {
    "EMAIL_NUDGE": {"cost": 5, "intensity": 0.2},
    "COUPON_10": {"cost": 50, "intensity": 0.5},
    "VIP_CALL": {"cost": 200, "intensity": 0.9},
}


# ------------------------------------------------------------
# Customer Type Simulation (Heterogeneity)
# ------------------------------------------------------------
CUSTOMER_TYPES = {
    "DISCOUNT_SENSITIVE": 1.3,
    "LOYAL_PREMIUM": 0.8,
    "CHURN_PRONE": 1.1,
    "PROMO_BLIND": 0.4,
}


def assign_customer_type(customer_id: int) -> str:
    """
    Synthetic segmentation assignment.
    Deterministic hash-based type mapping (stable per customer).
    """
    keys = list(CUSTOMER_TYPES.keys())
    return keys[customer_id % len(keys)]


# ------------------------------------------------------------
def simulate_uplift(customer: Dict, action: str) -> float:
    """
    Action-specific uplift simulator.

    Key realism:
    - customer heterogeneity
    - diminishing returns for strong interventions
    - negative uplift zones for promo-blind users
    """

    churn = float(customer["churn_prob"])
    cltv = float(customer["cltv"])
    intensity = ACTIONS[action]["intensity"]

    cust_type = assign_customer_type(customer["customer_id"])
    sensitivity = CUSTOMER_TYPES[cust_type]

    # --- base churn response ---
    churn_effect = churn * intensity * sensitivity

    # --- diminishing returns for very aggressive actions ---
    saturation = 1.0 / (1.0 + (intensity * 2))

    # --- CLTV scaling (high CLTV harder but worth it) ---
    value_factor = min(cltv / 80000, 1.0)

    uplift = churn_effect * saturation * (0.6 + 0.4 * value_factor)

    # --- Promo blind penalty ---
    if cust_type == "PROMO_BLIND" and action == "COUPON_10":
        uplift *= 0.2

    # --- noise injection (simulation realism) ---
    uplift += random.uniform(-0.02, 0.02)

    return round(max(min(uplift, 0.8), -0.1), 4)


# ------------------------------------------------------------
def choose_best_action(customer: Dict) -> Dict:
    """
    Evaluate all interventions and pick the profit-maximizing action.

    Returns:
    - offer
    - simulated uplift
    - expected profit
    - customer_type for explainability
    """

    cltv = float(customer["cltv"])
    best_offer, best_profit, best_uplift = None, -1e9, 0.0

    cust_type = assign_customer_type(customer["customer_id"])

    for action, meta in ACTIONS.items():
        cost = meta["cost"]
        uplift = simulate_uplift(customer, action)

        # Reject harmful interventions
        if uplift < 0:
            continue

        expected_gain = cltv * uplift
        net_profit = expected_gain - cost

        if net_profit > best_profit:
            best_offer = action
            best_profit = net_profit
            best_uplift = uplift

    return {
        "customer_id": customer["customer_id"],
        "customer_type": cust_type,
        "offer": best_offer,
        "uplift": best_uplift,
        "net_profit": round(best_profit, 2),
    }


# ------------------------------------------------------------
def build_policy(customers: List[Dict]) -> List[Dict]:
    """
    Assign best action for every customer.

    Output becomes input to ROI budget optimizer.
    """

    return [choose_best_action(c) for c in customers]
