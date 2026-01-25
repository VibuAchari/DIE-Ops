"""
src/models/train_churn.py

Enterprise-grade churn training script.

Trains a baseline churn propensity model (NOT uplift).
Key rules:
- Uses churn-safe features (no treatment leakage)
- Encodes segment + behavioral ratios
- Handles class imbalance properly
- Saves model + feature list in /models/
"""

import os
import joblib
import pandas as pd

from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score

from src.ingest.ingest import load_df
from src.validation.validate import validate_and_raise
from src.features.featurize import get_X_y

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(ROOT, "models")

CHURN_MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.pkl")
CHURN_FEATURES_PATH = os.path.join(MODEL_DIR, "churn_features.pkl")

RANDOM_STATE = 42


# ------------------------------------------------------------
def train_and_persist(test_size=0.2):
    """
    Train churn model and persist artifacts.
    """

    print("[train_churn] loading dataset...")
    df = load_df()

    print("[train_churn] validating dataset schema...")
    validate_and_raise(df)

    # ------------------------------------------------------------
    # Feature engineering (enterprise churn-safe)
    # ------------------------------------------------------------
    X, y, feature_cols = get_X_y(df, target_col="churned")

    # ------------------------------------------------------------
    # Train/Test Split (stratified)
    # ------------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=y
    )

    # ------------------------------------------------------------
    # LightGBM Classifier (enterprise config)
    # ------------------------------------------------------------
    model = LGBMClassifier(
        n_estimators=400,
        learning_rate=0.05,
        class_weight="balanced",   # IMPORTANT
        random_state=RANDOM_STATE
    )

    print("[train_churn] training LightGBM churn model...")
    model.fit(X_train, y_train)

    # ------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------
    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)

    auc = roc_auc_score(y_test, probs)
    precision = precision_score(y_test, preds)

    print(f"[train_churn] AUC: {auc:.4f}")
    print(f"[train_churn] Precision@0.5: {precision:.4f}")

    # ------------------------------------------------------------
    # Save artifacts
    # ------------------------------------------------------------
    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(model, CHURN_MODEL_PATH)
    joblib.dump(feature_cols, CHURN_FEATURES_PATH)

    print("[train_churn] saved churn model →", CHURN_MODEL_PATH)
    print("[train_churn] saved churn feature list →", CHURN_FEATURES_PATH)

    return CHURN_MODEL_PATH


# ------------------------------------------------------------
if __name__ == "__main__":
    train_and_persist()
