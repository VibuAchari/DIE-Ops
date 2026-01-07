# src/decision_engine/optimizer.py
"""
ROI-aware optimizer for campaign selection.

Key logic:
 - compute expected_gain = uplift * cltv * margin
 - filter customers where expected_gain > cost (simple profitability gate)
 - compute ROI = expected_gain / cost
 - greedy-select highest ROI until budget exhausted
 - produce CSV of selected recipients and return summary KPIs

This replaces the previous greedy_select and provides actionable outputs for reporting.
"""
import pandas as pd
import numpy as np
import os
from typing import Tuple, Dict

def compute_expected_gain(df: pd.DataFrame, margin: float) -> pd.DataFrame:
    """
    Expects df with columns: 'customer_id', 'uplift' (absolute prob uplift), 'cltv', 'cost'
    Adds 'expected_gain' and 'roi' columns and returns df copy.
    """
    df = df.copy()
    df["expected_gain"] = df["uplift"] * df["cltv"] * margin
    # avoid division by zero
    df["roi"] = df["expected_gain"] / df["cost"].replace(0, 1e-9)
    return df

def roi_select(df: pd.DataFrame, budget: float, margin: float = 0.30,
               min_profit_threshold: float = 0.0, export_csv: str = None
               ) -> Tuple[pd.DataFrame, Dict]:
    """
    Select customers under budget using ROI sorting, with a profitability gate.

    Parameters:
    - df: DataFrame with customer_id, uplift, cltv, cost
    - budget: total available budget (monetary)
    - margin: gross margin used to compute expected gain
    - min_profit_threshold: minimal expected_gain - cost required to consider a customer
    - export_csv: optional path to save selected recipients

    Returns:
    - selected_df: DataFrame of selected recipients with calculated fields
    - summary: dict with KPIs (selected_count, spent, expected_total_gain, avg_roi, avg_cost)
    """
    assert {"customer_id", "uplift", "cltv", "cost"}.issubset(set(df.columns)), "Required columns missing"

    # compute gains & roi
    scored = compute_expected_gain(df, margin)

    # profitability gate: expected gain must exceed cost + threshold
    scored["net_profit"] = scored["expected_gain"] - scored["cost"]
    scored = scored[scored["net_profit"] >= min_profit_threshold]

    # sort by ROI descending; tie-break by expected_gain
    scored = scored.sort_values(by=["roi", "expected_gain"], ascending=[False, False])

    selected_rows = []
    spent = 0.0
    for _, r in scored.iterrows():
        cost = float(r["cost"])
        if (spent + cost) <= float(budget):
            selected_rows.append(r)
            spent += cost
        else:
            continue

    if len(selected_rows) == 0:
        return pd.DataFrame(), {"selected_count": 0, "spent": 0.0, "expected_total_gain": 0.0}

    selected_df = pd.DataFrame(selected_rows).reset_index(drop=True)

    summary = {
        "selected_count": int(len(selected_df)),
        "spent": float(spent),
        "expected_total_gain": float(selected_df["expected_gain"].sum()),
        "avg_roi": float(selected_df["roi"].mean()),
        "avg_cost": float(selected_df["cost"].mean())
    }

    # export CSV for marketing ops if requested
    if export_csv:
        os.makedirs(os.path.dirname(export_csv) or ".", exist_ok=True)
        selected_df.to_csv(export_csv, index=False)
    return selected_df, summary
