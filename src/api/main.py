"""
src/api/main.py

DIE-Ops Customer Intelligence API (Enterprise-Stable)

Core signals:
- churn_prob → risk of leaving
- uplift     → churn reduction if treated
- cltv_raw   → monetary value
- optimizer  → selects best retention actions under budget

Endpoints:
- POST /score/customer
- POST /recommend
- GET  /simulate
"""

import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.ingest.ingest import load_df
from src.features.featurize import featurize_for_churn, featurize_for_uplift
from src.decision_engine.optimizer import roi_select
from src.decision_engine.actions import build_action_candidates


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(ROOT, "models")

CHURN_MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.pkl")
CHURN_FEATURES_PATH = os.path.join(MODEL_DIR, "churn_features.pkl")

UPLIFT_PATH = os.path.join(MODEL_DIR, "uplift_models.pkl")
CLTV_TABLE_PATH = os.path.join(MODEL_DIR, "cltv_table.csv")


# ------------------------------------------------------------
# FastAPI App
# ------------------------------------------------------------
app = FastAPI(title="DIE-Ops Customer Intelligence API")


# ------------------------------------------------------------
# Schemas
# ------------------------------------------------------------
class CustomerRequest(BaseModel):
    customer_id: int


class RecommendRequest(BaseModel):
    budget: float = 5000.0
    margin: float = 0.30


# ------------------------------------------------------------
# Startup Load
# ------------------------------------------------------------
@app.on_event("startup")
def load_artifacts():
    """
    Load dataset + models once at startup.
    """
    global churn_model, churn_features
    global treat_model, control_model
    global cltv_table, df_full

    print("[api] loading dataset...")
    df_full = load_df()

    print("[api] loading churn model...")
    churn_model = joblib.load(CHURN_MODEL_PATH)

    # ✅ Enforce churn feature schema
    churn_features = joblib.load(CHURN_FEATURES_PATH)

    print("[api] loading uplift models...")
    uplift = joblib.load(UPLIFT_PATH)
    treat_model = uplift["model_t"]
    control_model = uplift["model_c"]

    print("[api] loading CLTV table...")
    cltv_table = pd.read_csv(CLTV_TABLE_PATH)

    print("[api] startup complete ✅")


# ------------------------------------------------------------
# CLTV Lookup
# ------------------------------------------------------------
def lookup_cltv(customer_id: int) -> float:
    row = cltv_table[cltv_table["customer_id"] == customer_id]
    if row.empty:
        return 2000.0
    return float(row.iloc[0]["cltv_raw"])


# ------------------------------------------------------------
# Endpoint: Score Customer
# ------------------------------------------------------------
@app.post("/score/customer")
def score_customer(req: CustomerRequest):

    df = df_full[df_full["customer_id"] == req.customer_id].copy()
    if df.empty:
        raise HTTPException(status_code=404, detail="Customer not found")

    # ---- churn ----
    X_churn, _ = featurize_for_churn(df)

    # ✅ Align with training schema
    X_churn = X_churn[churn_features]

    churn_prob = float(churn_model.predict_proba(X_churn)[:, 1][0])

    # ---- uplift ----
    X_uplift, _ = featurize_for_uplift(df)

    p_t = float(treat_model.predict_proba(X_uplift)[:, 1][0])
    p_c = float(control_model.predict_proba(X_uplift)[:, 1][0])

    uplift = p_c - p_t

    # ---- cltv ----
    cltv_raw = lookup_cltv(req.customer_id)

    return {
        "customer_id": req.customer_id,
        "churn_prob": churn_prob,
        "uplift": uplift,
        "cltv_raw": cltv_raw
    }


# ------------------------------------------------------------
# Endpoint: Recommend Campaign Actions
# ------------------------------------------------------------
@app.post("/recommend")
def recommend(req: RecommendRequest):

    df = df_full.copy()

    # ---- churn scoring ----
    X_churn, _ = featurize_for_churn(df)
    X_churn = X_churn[churn_features]

    df["churn_prob"] = churn_model.predict_proba(X_churn)[:, 1]

    # ---- uplift scoring ----
    X_uplift, _ = featurize_for_uplift(df)

    p_t = treat_model.predict_proba(X_uplift)[:, 1]
    p_c = control_model.predict_proba(X_uplift)[:, 1]

    df["uplift"] = p_c - p_t

    # ---- attach CLTV ----
    df = df.merge(
        cltv_table[["customer_id", "cltv_raw"]],
        on="customer_id",
        how="left"
    )
    df["cltv_raw"] = df["cltv_raw"].fillna(2000)

    # --------------------------------------------------------
    # Action Expansion
    # --------------------------------------------------------
    candidates = build_action_candidates(df, margin=req.margin)

    if candidates.empty:
        return {"summary": {"selected_count": 0}, "selected_customers": []}

    # --------------------------------------------------------
    # ✅ One Best Offer Per Customer (SAFE selection)
    # --------------------------------------------------------
    best_idx = candidates.groupby("customer_id")["net_profit"].idxmax()
    candidates = candidates.loc[best_idx].reset_index(drop=True)

    # --------------------------------------------------------
    # ✅ ROI Efficiency Ranking (profit per rupee spent)
    # --------------------------------------------------------
    candidates["roi_ratio"] = candidates["net_profit"] / candidates["cost"]

    candidates = candidates.sort_values("roi_ratio", ascending=False)

    # --------------------------------------------------------
    # Budget Optimizer
    # --------------------------------------------------------
    selected_df, summary = roi_select(
        candidates,
        budget=req.budget,
        margin=req.margin
    )

    return {
        "summary": summary,
        "selected_customers": selected_df.head(200).to_dict(orient="records")
    }


# ------------------------------------------------------------
# Simulation Endpoint
# ------------------------------------------------------------
@app.get("/simulate")
def simulate(budget: float = 5000.0, margin: float = 0.30):
    req = RecommendRequest(budget=budget, margin=margin)
    return recommend(req)
