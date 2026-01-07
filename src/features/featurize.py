"""
src/features/featurize.py
Feature engineering helpers. Keep functions pure and deterministic for testability.
"""
import pandas as pd
import numpy as np

def basic_rfm_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute RFM-style features and some derived features used by models.
    Returns a new DataFrame with features plus customer_id.
    """
    df = df.copy()
    # Recency is already provided as days
    df["recency_log"] = np.log1p(df["recency_days"])
    df["frequency_log"] = np.log1p(df["frequency"])
    df["monetary_log"] = np.log1p(df["monetary"])
    df["avg_order_value"] = df["monetary"] / np.clip(df["frequency"].replace(0, 1), 1, None)
    # Tenure bucket
    df["tenure_bucket"] = pd.cut(df["tenure_days"], bins=[0, 180, 365, 730, 10000], labels=[0,1,2,3]).astype(int)
    # Simple affinity: last purchase relative to average
    df["last_vs_avg"] = df["last_purchase_amount"] / np.clip(df["avg_order_value"], 1e-6, None)
    # Fill infinite/nan if any
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
    return df[[
        "customer_id", "recency_days", "frequency", "monetary",
        "recency_log", "frequency_log", "monetary_log",
        "avg_order_value", "tenure_bucket", "last_vs_avg",
        "treatment", "churned"
    ]]


def featurize_for_scoring(df: pd.DataFrame) -> pd.DataFrame:
    """
    Produce a feature matrix for scoring (no label required).
    """
    feat = basic_rfm_features(df)
    feature_cols = ["recency_days", "frequency", "monetary",
                    "recency_log", "frequency_log", "monetary_log",
                    "avg_order_value", "tenure_bucket", "last_vs_avg", "treatment"]
    X = feat[["customer_id"] + feature_cols].copy()
    return X, feature_cols
