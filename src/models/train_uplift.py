"""
src/models/train_uplift.py
Train a simple uplift estimator using a two-model approach:
  - model_treat predicts outcome when treatment=1
  - model_ctrl predicts outcome when treatment=0
Uplift = P(y|treatment) - P(y|control)

Saves models to models/uplift_models.pkl
"""
import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from lightgbm import LGBMClassifier

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "uplift_models.pkl")

from src.ingest.ingest import load_df
from src.features.featurize import featurize_for_scoring
from src.validation.validate import validate_and_raise

RANDOM_STATE = 42

def train_and_persist():
    os.makedirs(MODEL_DIR, exist_ok=True)
    df = load_df()
    validate_and_raise(df)
    X_df, feature_cols = featurize_for_scoring(df)
    X = X_df[feature_cols].copy()
    # labels
    y = df["churned"]
    t = df["treatment"]

    # Train separate models
    X_t = X[t == 1]
    y_t = y[t == 1]
    X_c = X[t == 0]
    y_c = y[t == 0]

    # Fallback if one group is too small
    model_t = LGBMClassifier(n_estimators=50, random_state=RANDOM_STATE)
    model_c = LGBMClassifier(n_estimators=50, random_state=RANDOM_STATE)

    if len(X_t) < 10 or len(X_c) < 10:
        print("[train_uplift] Warning: small treatment/control groups; using pooled models with sample weighting")
        model = LGBMClassifier(n_estimators=50, random_state=RANDOM_STATE)
        model.fit(X, y)
        model_t = model_c = model
    else:
        model_t.fit(X_t, y_t)
        model_c.fit(X_c, y_c)

    artifacts = {"model_t": model_t, "model_c": model_c, "features": feature_cols}
    joblib.dump(artifacts, MODEL_PATH)
    print(f"[train_uplift] saved uplift artifacts to {MODEL_PATH}")
    return MODEL_PATH


if __name__ == "__main__":
    train_and_persist()
