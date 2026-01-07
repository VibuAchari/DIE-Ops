"""
DIE-Ops Modern FastAPI Backend
Exposes:
 - POST /score/customer
 - POST /score/batch
 - POST /recommend
 - GET  /simulate
Cleaned & aligned to the updated model architecture.
"""

import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(ROOT, "models")

CHURN_MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.pkl")
CHURN_FEATURES_PATH = os.path.join(MODEL_DIR, "churn_features.pkl")

UPLIFT_PATH = os.path.join(MODEL_DIR, "uplift_models.pkl")

CLTV_ARTIFACTS_PATH = os.path.join(MODEL_DIR, "cltv_artifacts.pkl")

DATA_PATH = os.path.join(ROOT, "data", "sample_customers.csv")

# ------------------------------------------------------------
# Local imports AFTER sys.path is correct
# ------------------------------------------------------------
from src.features.featurize import featurize_for_scoring
from src.decision_engine.optimizer import roi_select


app = FastAPI(title="DIE-Ops Customer Intelligence API")


# ------------------------------------------------------------
# Pydantic Input Models
# ------------------------------------------------------------
class CustomerScoreRequest(BaseModel):
    customer_id: int


class RecommendPayload(BaseModel):
    budget: float = 5000.0
    cost_per_action: float = 20.0
    margin: float = 0.30


# ------------------------------------------------------------
# Load models on startup
# ------------------------------------------------------------
@app.on_event("startup")
def load_models():
    global churn_model, churn_features
    global treat_model, control_model, uplift_features
    global cltv_bgf, cltv_ggf, cltv_scaler
    global df_full

    # Base dataset
    df_full = pd.read_csv(DATA_PATH)

    # Churn
    churn_model = joblib.load(CHURN_MODEL_PATH)
    churn_features = joblib.load(CHURN_FEATURES_PATH)

    # Uplift
    uplift = joblib.load(UPLIFT_PATH)
    treat_model = uplift["model_t"]
    control_model = uplift["model_c"]
    uplift_features = uplift["features"]

    # CLTV artifacts
    cltv = joblib.load(CLTV_ARTIFACTS_PATH)
    cltv_bgf = cltv["bgf"]
    cltv_ggf = cltv["ggf"]
    cltv_scaler = cltv["scaler"]


# ------------------------------------------------------------
# Internal scoring util
# ------------------------------------------------------------
def score_dataframe(df: pd.DataFrame):
    """
    Scores churn, uplift, CLTV for a given dataframe
    Returns the same df with new columns:
    - churn_prob
    - uplift
    - cltv
    """
    # Churn
    X = featurize_for_scoring(df, churn_features)
    df["churn_prob"] = churn_model.predict_proba(X)[:, 1]

    # Uplift
    X_u = featurize_for_scoring(df, uplift_features)
    p_t = treat_model.predict_proba(X_u)[:, 1]
    p_c = control_model.predict_proba(X_u)[:, 1]
    df["uplift"] = p_t - p_c

    # CLTV
    cltv_vals = cltv_ggf.customer_lifetime_value(
        cltv_bgf,
        df["frequency"],
        df["recency_days"],
        df["tenure_days"],
        df["monetary"],
        time=12,    # 12 months projection
        freq="D",
        discount_rate=0.01
    )
    df["cltv"] = cltv_scaler.transform(cltv_vals.values.reshape(-1, 1))

    return df


# ------------------------------------------------------------
# Single customer scoring
# ------------------------------------------------------------
@app.post("/score/customer")
def score_customer(req: CustomerScoreRequest):
    df = df_full[df_full["customer_id"] == req.customer_id].copy()
    if df.empty:
        raise HTTPException(status_code=404, detail="Customer not found")

    df = score_dataframe(df)

    row = df.iloc[0]
    return {
        "customer_id": int(row["customer_id"]),
        "churn_prob": float(row["churn_prob"]),
        "uplift": float(row["uplift"]),
        "cltv": float(row["cltv"]),
    }


# ------------------------------------------------------------
# Batch scoring
# ------------------------------------------------------------
@app.post("/score/batch")
def score_batch():
    df = df_full.copy()
    df = score_dataframe(df)
    return df[["customer_id", "churn_prob", "uplift", "cltv"]].to_dict(orient="records")


# ------------------------------------------------------------
# Recommendation Engine API
# ------------------------------------------------------------
@app.post("/recommend")
def recommend(payload: RecommendPayload):

    # score entire dataset
    df = score_dataframe(df_full.copy())

    # build decision frame
    dec = df[["customer_id", "uplift", "cltv"]].copy()
    dec["cost"] = payload.cost_per_action

    selected_df, summary = roi_select(
        dec,
        budget=payload.budget,
        margin=payload.margin,
        min_profit_threshold=0.0
    )

    return {
        "summary": summary,
        "selected": selected_df.head(200).to_dict(orient="records")
    }


# ------------------------------------------------------------
# Simulation endpoint
# ------------------------------------------------------------
@app.get("/simulate")
def simulate(budget: float = 5000, cost: float = 20.0, margin: float = 0.30):
    df = score_dataframe(df_full.copy())

    dec = df[["customer_id", "uplift", "cltv"]].copy()
    dec["cost"] = cost

    _, summary = roi_select(
        dec,
        budget=budget,
        margin=margin,
        min_profit_threshold=0.0
    )

    return {"summary": summary}
