"""
ingest.py
---------
Generates a synthetic enterprise-grade customer dataset with clean,
lifetimes-compatible fields for CLTV, churn, and uplift modeling.

Output:
 - data/sample_customers.csv
 - checksum for version traceability
"""

import os
import hashlib
import pandas as pd
import numpy as np


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(ROOT, "data")
OUT_PATH = os.path.join(DATA_DIR, "sample_customers.csv")


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def stable_hash(file_path):
    """Return an md5 checksum of a file."""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def generate_synthetic_customers(n=5000, seed=42):
    """
    DIE-Ops synthetic dataset generator (Decision-Intelligence aligned)

    Goals:
    - Realistic customer heterogeneity (segments)
    - Treatment has measurable effect (uplift is learnable)
    - Churn is probabilistic, not deterministic rules
    - Long-tail frequency + high CLTV customers exist

    Outputs compatible with:
    - churn model
    - uplift two-model baseline
    - lifetimes CLTV
    - ROI optimizer
    """
    rng = np.random.default_rng(seed)

    # ------------------------------------------------------------
    # 1. Customer Segments (enterprise realism)
    # ------------------------------------------------------------
    segment = rng.choice(
        ["low", "mid", "high"],
        size=n,
        p=[0.65, 0.25, 0.10]
    )

    # Tenure: 6 months – 4 years
    tenure_days = rng.integers(180, 1500, size=n)

    # Recency: time since last purchase (must <= tenure)
    recency_days = rng.integers(1, 365, size=n)
    recency_days = np.minimum(recency_days, tenure_days)

    # ------------------------------------------------------------
    # 2. Frequency (long-tail buyers)
    # ------------------------------------------------------------
    frequency = rng.poisson(3, size=n)

    # Heavy buyer boost for high segment
    heavy_mask = (segment == "high") & (rng.uniform(0, 1, size=n) < 0.6)
    frequency[heavy_mask] += rng.integers(10, 35, size=heavy_mask.sum())

    frequency = np.clip(frequency, 0, None)

    # ------------------------------------------------------------
    # 3. Monetary Value (segment-dependent spending)
    # ------------------------------------------------------------
    monetary = np.where(
        segment == "high",
        rng.normal(5500, 1400, size=n),
        np.where(
            segment == "mid",
            rng.normal(2500, 700, size=n),
            rng.normal(1200, 400, size=n)
        )
    )
    monetary = np.clip(monetary, 200, None)

    # Last purchase amount correlated with monetary
    last_purchase_amount = monetary * rng.uniform(0.7, 1.4, size=n)

    # ------------------------------------------------------------
    # 4. Treatment Assignment (campaign eligibility)
    # ------------------------------------------------------------
    treatment = rng.integers(0, 2, size=n)

    # ------------------------------------------------------------
    # 5. Base Churn Probability (not deterministic)
    # ------------------------------------------------------------
    # Core churn drivers:
    # - inactivity (recency)
    # - low engagement (frequency)
    # - low value customers churn more
    # - random shocks exist

    base_risk = (
        0.45 * (recency_days / 365) +
        0.35 * (1 / (1 + frequency)) +
        0.20 * (segment == "low").astype(int)
    )

    # Add stochastic noise (enterprise unpredictability)
    base_risk += rng.normal(0, 0.05, size=n)

    # Convert into churn probability
    churn_prob = 1 / (1 + np.exp(-4 * (base_risk - 0.55)))
    churn_prob = np.clip(churn_prob, 0.02, 0.85)

    # ------------------------------------------------------------
    # 6. Treatment Effect (uplift must exist!)
    # ------------------------------------------------------------
    # Treatment reduces churn, stronger effect for mid/high customers
    treatment_effect = np.where(
        treatment == 1,
        np.where(segment == "high", -0.18,
        np.where(segment == "mid", -0.12, -0.06)),
        0.0
    )

    churn_prob_treated = np.clip(churn_prob + treatment_effect, 0.01, 0.90)

    # Final churn outcome
    churned = (rng.uniform(0, 1, size=n) < churn_prob_treated).astype(int)

    # ------------------------------------------------------------
    # 7. Build DataFrame
    # ------------------------------------------------------------
    df = pd.DataFrame({
        "customer_id": np.arange(1, n + 1),
        "segment": segment,
        "recency_days": recency_days,
        "frequency": frequency,
        "monetary": monetary,
        "tenure_days": tenure_days,
        "last_purchase_amount": last_purchase_amount,
        "treatment": treatment,
        "churned": churned
    })

    return df



def save_dataset(df, path=OUT_PATH):
    ensure_dir(os.path.dirname(path))
    df.to_csv(path, index=False)
    print(f"[ingest] Saved dataset to {path}")
    return stable_hash(path)


def load_df():
    """Convenience loader for API/backend."""
    if not os.path.exists(OUT_PATH):
        raise FileNotFoundError("[ingest] Dataset missing. Run ingest.py first.")
    return pd.read_csv(OUT_PATH)


def main():
    if os.path.exists(OUT_PATH):
        print(f"[ingest] dataset already exists at {OUT_PATH}")
        print(f"[ingest] checksum: {stable_hash(OUT_PATH)}")
        return

    print("[ingest] generating synthetic dataset...")
    df = generate_synthetic_customers()

    checksum = save_dataset(df, OUT_PATH)
    print(f"[ingest] checksum: {checksum}")


if __name__ == "__main__":
    main()
