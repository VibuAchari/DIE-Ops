"""
src/api/main.py

DIE-Ops Decision Intelligence API (Enterprise-Stable)

Core signals:
- churn_prob → churn risk
- uplift     → expected churn reduction if treated
- cltv_raw   → customer value
- optimizer  → budget-constrained ROI action selector

Endpoints:
- POST /score/customer
- GET  /policy/options/{customer_id}
- GET  /policy/decision/{customer_id}
- POST /campaign/recommend
- GET  /simulate
"""

import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.ingest.ingest import load_df
from src.features.featurize import featurize_for_churn, featurize_for_uplift

from src.decision_engine.actions import build_action_candidates
from src.decision_engine.optimizer import roi_select

from src.api.report import router as report_router


# ============================================================
# Paths
# ============================================================

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(ROOT, "models")

CHURN_MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.pkl")
CHURN_FEATURES_PATH = os.path.join(MODEL_DIR, "churn_features.pkl")

UPLIFT_PATH = os.path.join(MODEL_DIR, "uplift_models.pkl")
CLTV_TABLE_PATH = os.path.join(MODEL_DIR, "cltv_table.csv")


# ============================================================
# App
# ============================================================

app = FastAPI(title="DIE-Ops Decision Intelligence API")


# ============================================================
# Request Schemas
# ============================================================

class CustomerRequest(BaseModel):
    customer_id: int


class CampaignRequest(BaseModel):
    budget: float = 5000.0
    margin: float = 0.30


# ============================================================
# Startup Load
# ============================================================

@app.on_event("startup")
def load_artifacts():
    """
    Loads dataset + models ONCE.
    """
    global churn_model, churn_features
    global treat_model, control_model
    global cltv_table, df_full

    print("\n[api] loading dataset...")
    df_full = load_df()

    print("[api] loading churn model...")
    churn_model = joblib.load(CHURN_MODEL_PATH)
    churn_features = joblib.load(CHURN_FEATURES_PATH)

    print("[api] loading uplift models...")
    uplift = joblib.load(UPLIFT_PATH)
    treat_model = uplift["model_t"]
    control_model = uplift["model_c"]

    print("[api] loading CLTV table...")
    cltv_table = pd.read_csv(CLTV_TABLE_PATH)

    print("[api] startup complete ✅\n")


# ============================================================
# Internal: Stable Customer Scoring
# ============================================================

def score_customer_row(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds churn_prob + uplift + cltv_raw into df.
    Output is ALWAYS schema-stable.
    """

    # ---- churn ----
    X_churn, _ = featurize_for_churn(df)
    X_churn = X_churn[churn_features]

    df["churn_prob"] = churn_model.predict_proba(X_churn)[:, 1]

    # ---- uplift ----
    X_uplift, _ = featurize_for_uplift(df)

    p_t = treat_model.predict_proba(X_uplift)[:, 1]
    p_c = control_model.predict_proba(X_uplift)[:, 1]

    df["uplift"] = p_c - p_t

    # ---- cltv ----
    df = df.merge(
        cltv_table[["customer_id", "cltv_raw"]],
        on="customer_id",
        how="left"
    )

    df["cltv_raw"] = df["cltv_raw"].fillna(2000)

    return df


# ============================================================
# Schema Normalizer (PDF + Narratives Contract)
# ============================================================

REQUIRED_FIELDS = [
    "customer_id",
    "offer",
    "cost",
    "net_profit",
    "churn_prob",
    "uplift",
    "cltv_raw"
]

def enforce_pdf_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Forces campaign output into locked PDF schema.
    Prevents ALL downstream drift.
    """

    for col in REQUIRED_FIELDS:
        if col not in df.columns:
            df[col] = 0

    # type enforcement
    df["customer_id"] = df["customer_id"].astype(int)
    df["cost"] = df["cost"].astype(float)
    df["net_profit"] = df["net_profit"].astype(float)

    return df


# ============================================================
# Endpoint: Score One Customer
# ============================================================

@app.post("/score/customer")
def score_customer(req: CustomerRequest):

    df = df_full[df_full["customer_id"] == req.customer_id].copy()

    if df.empty:
        raise HTTPException(status_code=404, detail="Customer not found")

    df = score_customer_row(df)

    row = df.iloc[0]

    return {
        "customer_id": int(row["customer_id"]),
        "churn_prob": float(row["churn_prob"]),
        "uplift": float(row["uplift"]),
        "cltv_raw": float(row["cltv_raw"]),
    }


# ============================================================
# Endpoint: Policy Options Per Customer
# ============================================================

@app.get("/policy/options/{customer_id}")
def policy_options(customer_id: int):

    df = df_full[df_full["customer_id"] == customer_id].copy()

    if df.empty:
        raise HTTPException(status_code=404, detail="Customer not found")

    df = score_customer_row(df)

    candidates = build_action_candidates(df, margin=0.30)

    if candidates.empty:
        return {"customer_id": customer_id, "options": []}

    candidates = enforce_pdf_schema(candidates)

    return {
        "customer_id": customer_id,
        "options": candidates.to_dict(orient="records")
    }


# ============================================================
# Endpoint: Best Policy Decision Per Customer
# ============================================================

@app.get("/policy/decision/{customer_id}")
def policy_decision(customer_id: int):

    options = policy_options(customer_id)

    if not options["options"]:
        return {
            "customer_id": customer_id,
            "decision": None,
            "reason": "No profitable intervention available."
        }

    df = pd.DataFrame(options["options"])

    best = df.sort_values("net_profit", ascending=False).iloc[0]

    return {
        "customer_id": customer_id,
        "decision": {
            "offer": best["offer"],
            "cost": float(best["cost"]),
            "net_profit": float(best["net_profit"]),
            "roi_ratio": float(best["net_profit"] / best["cost"])
        },
        "justification": (
            "Policy selects the action that maximizes expected profit "
            "among all available interventions."
        )
    }


# ============================================================
# Endpoint: Campaign Recommendation (Budget Optimized)
# ============================================================

@app.post("/campaign/recommend")
def recommend_campaign(req: CampaignRequest):

    # ---- Score all customers ----
    df = score_customer_row(df_full.copy())

    # ---- Expand all action candidates ----
    candidates = build_action_candidates(df, margin=req.margin)

    if candidates.empty:
        return {
            "summary": {
                "selected_count": 0,
                "budget_used": 0,
                "expected_profit": 0,
                "avg_profit_per_customer": 0,
            },
            "selected_customers": []
        }

    # ---- One best offer per customer ----
    best_idx = candidates.groupby("customer_id")["net_profit"].idxmax()
    candidates = candidates.loc[best_idx].reset_index(drop=True)

    # ---- ROI ranking ----
    candidates["roi_ratio"] = candidates["net_profit"] / candidates["cost"]
    candidates = candidates.sort_values("roi_ratio", ascending=False)

    # ---- Budget optimizer ----
    selected_df, _ = roi_select(
        candidates,
        budget=req.budget,
        margin=req.margin
    )

    selected_df = enforce_pdf_schema(selected_df)

    selected_customers = selected_df.head(200).to_dict(orient="records")

    # ---- Locked PDF Summary ----
    selected_count = len(selected_customers)
    expected_profit = float(selected_df["net_profit"].sum())
    budget_used = float(selected_df["cost"].sum())

    summary = {
        "selected_count": selected_count,
        "budget_used": budget_used,
        "expected_profit": expected_profit,
        "avg_profit_per_customer": (
            expected_profit / selected_count if selected_count else 0
        )
    }

    return {
        "summary": summary,
        "selected_customers": selected_customers
    }


# ============================================================
# Simulation Shortcut
# ============================================================

@app.get("/simulate")
def simulate(budget: float = 5000.0, margin: float = 0.30):
    req = CampaignRequest(budget=budget, margin=margin)
    return recommend_campaign(req)


# ============================================================
# Register Report Router
# ============================================================

app.include_router(report_router)