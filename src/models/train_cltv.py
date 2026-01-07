"""
train_cltv.py
Trains a probabilistic CLTV model using:
 - BetaGeoFitter (BGF) for frequency/recency
 - GammaGammaFitter (GGF) for monetary value
Outputs:
 - bgf model
 - ggf model
 - scaler for normalization
Saved to: models/cltv_artifacts.pkl
"""

import os
import joblib
import pandas as pd
from lifetimes import BetaGeoFitter, GammaGammaFitter
from sklearn.preprocessing import MinMaxScaler

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(ROOT, "models")
DATA_PATH = os.path.join(ROOT, "data", "sample_customers.csv")
OUTPUT_PATH = os.path.join(MODEL_DIR, "cltv_artifacts.pkl")


def train_and_persist():
    df = pd.read_csv(DATA_PATH)

    # Required lifetimes columns
    frequency = df["frequency"]
    recency = df["recency_days"]
    tenure = df["tenure_days"]
    monetary = df["monetary"]

    # Fit BGF model
    bgf = BetaGeoFitter(penalizer_coef=0.01)
    bgf.fit(frequency, recency, tenure)

    # Fit GGF model
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(frequency, monetary)

    # Predict 12-month CLTV
    cltv = ggf.customer_lifetime_value(
        bgf,
        frequency,
        recency,
        tenure,
        monetary,
        time=12,
        freq="D",
        discount_rate=0.01
    )

    # Scale for ML compatibility
    scaler = MinMaxScaler()
    cltv_scaled = scaler.fit_transform(cltv.values.reshape(-1, 1))

    # Save all pieces
    artifacts = {
        "bgf": bgf,
        "ggf": ggf,
        "scaler": scaler,
    }

    joblib.dump(artifacts, OUTPUT_PATH)
    print("[train_cltv] Saved CLTV artifacts to:", OUTPUT_PATH)


if __name__ == "__main__":
    train_and_persist()
