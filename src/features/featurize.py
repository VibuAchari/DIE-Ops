"""
src/features/featurize.py
Enterprise-grade deterministic feature engineering for DIE-Ops.

Design rules:
- No label leakage inside feature functions
- Segment must be encoded
- Treatment is excluded from churn baseline features (used only in uplift)
- Add behavioral ratios: engagement decay + intensity
"""

import pandas as pd
import numpy as np


# -------------------------------
# Core deterministic feature builder
# -------------------------------
def build_customer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build enterprise-style customer behavioral features.
    Returns ONLY features + customer_id (no labels).
    """

    df = df.copy()

    # -------------------------------
    # Log transforms (stability)
    # -------------------------------
    df["recency_log"] = np.log1p(df["recency_days"])
    df["frequency_log"] = np.log1p(df["frequency"])
    df["monetary_log"] = np.log1p(df["monetary"])

    # -------------------------------
    # Spend intensity & engagement velocity
    # -------------------------------
    df["avg_order_value"] = df["monetary"] / np.clip(df["frequency"], 1, None)

    # Frequency per year of tenure (purchase velocity)
    df["purchase_velocity"] = df["frequency"] / np.clip(df["tenure_days"] / 365.0, 0.1, None)

    # Recency relative to tenure (inactivity ratio)
    df["recency_ratio"] = df["recency_days"] / np.clip(df["tenure_days"], 1, None)

    # Last purchase deviation
    df["last_vs_avg"] = df["last_purchase_amount"] / np.clip(df["avg_order_value"], 1e-6, None)

    # -------------------------------
    # Tenure bucket (coarse lifecycle)
    # -------------------------------
    df["tenure_bucket"] = pd.cut(
        df["tenure_days"],
        bins=[0, 180, 365, 730, 2000],
        labels=[0, 1, 2, 3]
    ).astype(int)

    # -------------------------------
    # Segment encoding (IMPORTANT)
    # -------------------------------
    if "segment" in df.columns:
        df["segment_low"] = (df["segment"] == "low").astype(int)
        df["segment_mid"] = (df["segment"] == "mid").astype(int)
        df["segment_high"] = (df["segment"] == "high").astype(int)
    else:
        # fallback if segment missing
        df["segment_low"] = 0
        df["segment_mid"] = 0
        df["segment_high"] = 0

    # -------------------------------
    # Clean infinities/nans
    # -------------------------------
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0)

    return df[
        [
            "customer_id",

            # Core RFM
            "recency_days",
            "frequency",
            "monetary",

            # Transforms
            "recency_log",
            "frequency_log",
            "monetary_log",

            # Behavioral ratios
            "avg_order_value",
            "purchase_velocity",
            "recency_ratio",
            "last_vs_avg",

            # Lifecycle
            "tenure_bucket",

            # Segment one-hot
            "segment_low",
            "segment_mid",
            "segment_high",
        ]
    ]


# -------------------------------
# Churn scoring features (NO treatment)
# -------------------------------
def featurize_for_churn(df: pd.DataFrame):
    """
    Feature matrix for churn model.
    Excludes treatment to avoid leakage.
    """
    X = build_customer_features(df)

    feature_cols = [c for c in X.columns if c != "customer_id"]
    return X[feature_cols], feature_cols


# -------------------------------
# Uplift scoring features (treatment allowed)
# -------------------------------
def featurize_for_uplift(df: pd.DataFrame):
    """
    Feature matrix for uplift model.
    Includes treatment as intervention flag.
    """
    X = build_customer_features(df)

    # add treatment explicitly
    X["treatment"] = df["treatment"].astype(int)

    feature_cols = [c for c in X.columns if c != "customer_id"]
    return X[feature_cols], feature_cols


# -------------------------------
# Training utility: X,y
# -------------------------------
def get_X_y(df: pd.DataFrame, target_col="churned"):
    """
    Extract X,y safely for churn training.
    """
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' missing")

    X, feature_cols = featurize_for_churn(df)
    y = df[target_col].astype(int)

    return X, y, feature_cols
