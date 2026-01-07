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


def generate_synthetic_customers(n=4000, seed=42):
    """
    Generate high-quality synthetic customer data that satisfies
    lifetimes and model constraints.

    Fields:
      customer_id
      recency_days
      frequency
      monetary
      tenure_days
      last_purchase_amount
      treatment
    """
    rng = np.random.default_rng(seed)

    # 1. Tenure distribution: customers acquired anytime in last 2-4 years
    tenure_days = rng.integers(200, 1500, size=n)

    # 2. Recency distribution: time since last purchase
    #    Must ALWAYS satisfy recency <= tenure
    recency_days = rng.integers(1, 300, size=n)
    recency_days = np.minimum(recency_days, tenure_days)

    # 3. Frequency: purchases made
    #    Some heavy buyers, lots of light buyers
    frequency = rng.poisson(3, size=n)
    frequency[frequency < 0] = 0  # safety

    # 4. Monetary: avg purchase amount
    monetary = rng.normal(2000, 600, size=n)
    monetary = np.clip(monetary, 100, None)  # CLTV requires positive >

    # 5. Last purchase amount correlated with monetary + noise
    last_purchase_amount = monetary * rng.uniform(0.8, 1.3, size=n)

    # 6. Treatment indicator (for uplift demo)
    treatment = rng.integers(0, 2, size=n)

    df = pd.DataFrame({
        "customer_id": np.arange(1, n + 1),
        "recency_days": recency_days,
        "frequency": frequency,
        "monetary": monetary,
        "tenure_days": tenure_days,
        "last_purchase_amount": last_purchase_amount,
        "treatment": treatment
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
