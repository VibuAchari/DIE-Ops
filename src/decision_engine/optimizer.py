"""
src/decision_engine/optimizer.py

Enterprise ROI Optimizer for Campaign Target Selection

Core logic:
- expected_gain = churn_prob * uplift * cltv * margin
- net_profit    = expected_gain - cost
- select highest net_profit customers under budget

Maximizes business impact, not probability scores.
"""

import pandas as pd
import os
from typing import Tuple, Dict


# ------------------------------------------------------------
def score_candidates(df: pd.DataFrame, margin: float) -> pd.DataFrame:
    """
    Adds decision economics if missing.

    Required columns:
    - customer_id
    - uplift
    - cltv
    - cost

    Optional:
    - churn_prob
    - expected_gain (if already computed upstream)
    """

    df = df.copy()

    # If expected_gain not provided, compute it
    if "expected_gain" not in df.columns:

        churn_factor = df["churn_prob"] if "churn_prob" in df.columns else 1.0

        df["expected_gain"] = (
            churn_factor *
            df["uplift"] *
            df["cltv"] *
            margin
        )

    # Net profit
    df["net_profit"] = df["expected_gain"] - df["cost"]

    return df


# ------------------------------------------------------------
def roi_select(
    df: pd.DataFrame,
    budget: float,
    margin: float = 0.30,
    min_profit_threshold: float = 0.0,
    export_csv: str = None
) -> Tuple[pd.DataFrame, Dict]:
    """
    Campaign target selection under budget.

    Steps:
    - compute expected gain + net profit
    - drop unprofitable customers
    - rank by net_profit descending
    - greedy pick until budget exhausted
    """

    required = {"customer_id", "uplift", "cltv", "cost"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required - set(df.columns)}")

    # Score economics
    scored = score_candidates(df, margin)

    # Profitability gate
    scored = scored[scored["net_profit"] > min_profit_threshold]

    # Sort by impact
    scored = scored.sort_values("net_profit", ascending=False)

    # Greedy budget allocation
    selected = []
    spent = 0.0

    for _, row in scored.iterrows():
        cost = float(row["cost"])
        if spent + cost <= budget:
            selected.append(row)
            spent += cost

    if not selected:
        return pd.DataFrame(), {
            "selected_count": 0,
            "spent": 0.0,
            "expected_total_gain": 0.0,
            "expected_total_profit": 0.0
        }

    selected_df = pd.DataFrame(selected).reset_index(drop=True)

    summary = {
        "selected_count": int(len(selected_df)),
        "spent": float(spent),
        "expected_total_gain": float(selected_df["expected_gain"].sum()),
        "expected_total_profit": float(selected_df["net_profit"].sum()),
        "avg_profit_per_customer": float(selected_df["net_profit"].mean())
    }

    # Optional export
    if export_csv:
        os.makedirs(os.path.dirname(export_csv) or ".", exist_ok=True)
        selected_df.to_csv(export_csv, index=False)

    return selected_df, summary
