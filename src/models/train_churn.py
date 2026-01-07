"""
src/models/train_churn.py
Train a churn classifier (LightGBM) on the synthetic dataset.
Saves model artifact to models/churn_model.pkl
Also saves a simple calibration function and feature list.
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score
from lightgbm import LGBMClassifier

# Paths
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(ROOT, "data", "sample_customers.csv")
MODEL_DIR = os.path.join(ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.pkl")
FEATURES_PATH = os.path.join(MODEL_DIR, "churn_features.pkl")

from src.features.featurize import featurize_for_scoring
from src.validation.validate import validate_and_raise
from src.ingest.ingest import load_df

RANDOM_STATE = 42


def train_and_persist(test_size=0.2):
    os.makedirs(MODEL_DIR, exist_ok=True)
    # Load
    df = load_df()
    validate_and_raise(df)
    X_df, feature_cols = featurize_for_scoring(df)
    X = X_df[feature_cols]
    y = df["churned"]

    # Time-ordered split is more realistic, but data is synthetic; we do stratified split here
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=RANDOM_STATE, stratify=y)

    # LightGBM classifier
    clf = LGBMClassifier(n_estimators=100, random_state=RANDOM_STATE)
    clf.fit(X_train, y_train)

    # Metrics
    preds = clf.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, preds)
    precision_at_0_5 = precision_score(y_test, (preds >= 0.5).astype(int))
    print(f"[train_churn] AUC: {auc:.4f}, Precision@0.5: {precision_at_0_5:.4f}")

    # Persist
    joblib.dump(clf, MODEL_PATH)
    joblib.dump(feature_cols, FEATURES_PATH)
    print(f"[train_churn] saved model to {MODEL_PATH}")

    return MODEL_PATH


if __name__ == "__main__":
    train_and_persist()
