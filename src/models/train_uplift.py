"""
src/models/train_uplift.py

Enterprise-grade uplift estimation (Two-Model Approach)

Trains:
 - model_t: predicts churn probability under treatment
 - model_c: predicts churn probability under control

Uplift = P(churn|control) - P(churn|treatment)

Artifacts saved:
 - models/uplift_models.pkl
"""

import os
import joblib
import pandas as pd

from lightgbm import LGBMClassifier

from src.ingest.ingest import load_df
from src.validation.validate import validate_and_raise
from src.features.featurize import featurize_for_uplift


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "uplift_models.pkl")

RANDOM_STATE = 42


# ------------------------------------------------------------
def train_and_persist():
    """
    Train uplift models and persist.
    """

    print("[train_uplift] loading dataset...")
    df = load_df()
    validate_and_raise(df)

    # ------------------------------------------------------------
    # Feature engineering (uplift-safe, includes treatment flag)
    # ------------------------------------------------------------
    X, feature_cols = featurize_for_uplift(df)

    # Target = churn outcome
    y = df["churned"].astype(int)

    # Treatment indicator
    t = df["treatment"].astype(int)

    # ------------------------------------------------------------
    # Split treatment and control groups
    # ------------------------------------------------------------
    X_treat = X[t == 1]
    y_treat = y[t == 1]

    X_ctrl = X[t == 0]
    y_ctrl = y[t == 0]

    print(f"[train_uplift] Treatment group size: {len(X_treat)}")
    print(f"[train_uplift] Control group size:   {len(X_ctrl)}")

    # ------------------------------------------------------------
    # Models (balanced, enterprise config)
    # ------------------------------------------------------------
    model_t = LGBMClassifier(
        n_estimators=300,
        learning_rate=0.05,
        class_weight="balanced",
        random_state=RANDOM_STATE
    )

    model_c = LGBMClassifier(
        n_estimators=300,
        learning_rate=0.05,
        class_weight="balanced",
        random_state=RANDOM_STATE
    )

    # ------------------------------------------------------------
    # Train models
    # ------------------------------------------------------------
    print("[train_uplift] training model_t (treated)...")
    model_t.fit(X_treat, y_treat)

    print("[train_uplift] training model_c (control)...")
    model_c.fit(X_ctrl, y_ctrl)

    # ------------------------------------------------------------
    # Save artifacts
    # ------------------------------------------------------------
    artifacts = {
        "model_t": model_t,
        "model_c": model_c,
        "features": feature_cols
    }

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(artifacts, MODEL_PATH)

    print("[train_uplift] saved uplift models →", MODEL_PATH)
    return MODEL_PATH


# ------------------------------------------------------------
if __name__ == "__main__":
    train_and_persist()
