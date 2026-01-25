"""
DIE-Ops Unified Application (app.py)

This file consolidates the entire source code of the DIE-Ops project into a single production-ready script.
It includes:
- Data Ingestion & Generation
- Feature Engineering
- Model Training (Churn, CLTV, Uplift)
- Validation & Utils
- Decision Engine & Optimizer
- Report Generation
- FastAPI Backend
- Flask Frontend
- Streamlit Dashboard

Usage:
  1. Install dependencies: pip install -r requirements.txt
  2. Data Ingest:      python app.py ingest
  3. Train Models:     python app.py train
  4. Run API:          python app.py api       (Runs FastAPI on port 8000)
"""

import os
import sys
import json
import joblib
import hashlib
import datetime
import argparse
import numpy as np
import pandas as pd
import requests
import shap
from typing import List, Dict, Tuple, Optional

# Framework Imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from flask import Flask, render_template, request as flask_request, jsonify
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score
from sklearn.preprocessing import MinMaxScaler
from lifetimes import BetaGeoFitter, GammaGammaFitter

# Streamlit Check removed


# ----------------------------------------------------------------------------
# CONFIGURATION & CONSTANTS
# ----------------------------------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
MODEL_DIR = os.path.join(ROOT_DIR, "models")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")

DATA_PATH = os.path.join(DATA_DIR, "sample_customers.csv")

# Model Paths
CHURN_MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.pkl")
CHURN_FEATURES_PATH = os.path.join(MODEL_DIR, "churn_features.pkl")
UPLIFT_PATH = os.path.join(MODEL_DIR, "uplift_models.pkl")
CLTV_ARTIFACTS_PATH = os.path.join(MODEL_DIR, "cltv_artifacts.pkl")

# API Configuration
API_URL_LOCAL = "http://127.0.0.1:8000"

RANDOM_STATE = 42

# ----------------------------------------------------------------------------
# UTILITIES (src/utils/helpers.py, src/validation/validate.py)
# ----------------------------------------------------------------------------
def ensure_dirs(path_list):
    for p in path_list:
        os.makedirs(p, exist_ok=True)

def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

def load_joblib(path):
    return joblib.load(path)

# Ensure core directories exist
ensure_dirs([DATA_DIR, MODEL_DIR, OUTPUT_DIR])

def basic_schema_checks(df: pd.DataFrame) -> Tuple[bool, Dict]:
    required_cols = {"customer_id", "recency_days", "frequency", "monetary", "tenure_days", "churned", "treatment"}
    details = {}
    missing = required_cols.difference(set(df.columns))
    if missing:
        details["missing_columns"] = list(missing)
        return False, details

    null_counts = df[list(required_cols)].isnull().sum().to_dict()
    details["null_counts"] = null_counts
    if any(v > 0 for v in null_counts.values()):
        details["valid"] = False
        return False, details

    details["dtypes"] = df[list(required_cols)].dtypes.astype(str).to_dict()
    details["valid"] = True
    return True, details

def validate_and_raise(df: pd.DataFrame):
    valid, details = basic_schema_checks(df)
    if not valid:
        raise ValueError(f"Validation failed: {details}")
    return details

# ----------------------------------------------------------------------------
# INGEST (src/ingest/ingest.py)
# ----------------------------------------------------------------------------
def stable_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def generate_synthetic_customers(n=4000, seed=42):
    rng = np.random.default_rng(seed)
    
    # 1. Tenure: 200 to 1500 days
    tenure_days = rng.integers(200, 1500, size=n)
    
    # 2. Recency: <= Tenure
    recency_days = rng.integers(1, 300, size=n)
    recency_days = np.minimum(recency_days, tenure_days)
    
    # 3. Frequency
    frequency = rng.poisson(3, size=n)
    frequency[frequency < 0] = 0
    
    # 4. Monetary
    monetary = rng.normal(2000, 600, size=n)
    monetary = np.clip(monetary, 100, None)
    
    # 5. Last Purchase
    last_purchase_amount = monetary * rng.uniform(0.8, 1.3, size=n)
    
    # 6. Treatment (for uplift)
    treatment = rng.integers(0, 2, size=n)
    
    # 7. Churn Label (Synthetic Logic for correlation)
    # Higher recency (inactive for long) -> Higher churn risk
    # Higher frequency -> Lower churn risk
    churn_prob = (recency_days / 365.0) * 0.7 - (frequency * 0.05)
    churn_prob = np.clip(churn_prob, 0.1, 0.9)
    churned = rng.binomial(1, churn_prob)
    
    df = pd.DataFrame({
        "customer_id": np.arange(1, n + 1),
        "recency_days": recency_days,
        "frequency": frequency,
        "monetary": monetary,
        "tenure_days": tenure_days,
        "last_purchase_amount": last_purchase_amount,
        "treatment": treatment,
        "churned": churned
    })
    return df

def run_ingest():
    if os.path.exists(DATA_PATH):
        print(f"[ingest] Dataset already exists at {DATA_PATH}")
        return
    print("[ingest] Generating synthetic dataset...")
    df = generate_synthetic_customers()
    ensure_dirs([os.path.dirname(DATA_PATH)])
    df.to_csv(DATA_PATH, index=False)
    print(f"[ingest] Saved dataset to {DATA_PATH}")

def load_df():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("[ingest] Dataset missing. Run ingest first.")
    return pd.read_csv(DATA_PATH)

# ----------------------------------------------------------------------------
# FEATURIZATION (src/features/featurize.py)
# ----------------------------------------------------------------------------
def basic_rfm_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["recency_log"] = np.log1p(df["recency_days"])
    df["frequency_log"] = np.log1p(df["frequency"])
    df["monetary_log"] = np.log1p(df["monetary"])
    df["avg_order_value"] = df["monetary"] / np.clip(df["frequency"].replace(0, 1), 1, None)
    df["tenure_bucket"] = pd.cut(df["tenure_days"], bins=[0, 180, 365, 730, 10000], labels=[0,1,2,3]).astype(int)
    df["last_vs_avg"] = df["last_purchase_amount"] / np.clip(df["avg_order_value"], 1e-6, None)
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    cols = [
        "customer_id", "recency_days", "frequency", "monetary",
        "recency_log", "frequency_log", "monetary_log",
        "avg_order_value", "tenure_bucket", "last_vs_avg",
        "treatment"
    ]
    if "churned" in df.columns:
        cols.append("churned")
    return df[cols]

def featurize_for_scoring(df: pd.DataFrame, feature_cols: List[str] = None) -> Tuple[pd.DataFrame, List[str]]:
    feat = basic_rfm_features(df)
    
    # Default feature list if not provided
    if feature_cols is None:
        feature_cols = ["recency_days", "frequency", "monetary",
                        "recency_log", "frequency_log", "monetary_log",
                        "avg_order_value", "tenure_bucket", "last_vs_avg", "treatment"]
    
    # Ensure all columns exist
    for c in feature_cols:
        if c not in feat.columns:
            feat[c] = 0
            
    X = feat[["customer_id"] + feature_cols].copy()
    return X, feature_cols

# ----------------------------------------------------------------------------
# EXPLAINABILITY (src/explain/shap_narrative.py)
# ----------------------------------------------------------------------------
def narrative_from_shap(model, X_row, feature_cols, top_k=3):
    try:
        explainer = shap.Explainer(model.predict_proba, X_row)
        shap_vals = explainer(X_row)
        if hasattr(shap_vals, "values"):
            vals = np.array(shap_vals.values)
            if vals.ndim == 3:
                contribs = vals[0, :, 1]
            else:
                contribs = vals[0, :]
        else:
            contribs = shap_vals.values[0]

        feature_importance = sorted(zip(feature_cols, contribs), key=lambda x: -abs(x[1]))[:top_k]
        parts = []
        for f, v in feature_importance:
            sign = "increases" if v > 0 else "decreases"
            parts.append(f"{f} {sign} risk (impact {v:.3f})")
        return "Top drivers: " + "; ".join(parts) + "."
    except Exception as e:
        return f"Explanation not available: {e}"

# ----------------------------------------------------------------------------
# TRAINING (src/models/*.py)
# ----------------------------------------------------------------------------
def train_churn(test_size=0.2):
    print("[train] Starting Churn Training...")
    df = load_df()
    validate_and_raise(df)
    X_df, feature_cols = featurize_for_scoring(df)
    X = X_df[feature_cols]
    y = df["churned"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=RANDOM_STATE, stratify=y)
    clf = LGBMClassifier(n_estimators=100, random_state=RANDOM_STATE)
    clf.fit(X_train, y_train)
    
    preds = clf.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, preds)
    print(f"[train_churn] AUC: {auc:.4f}")
    
    joblib.dump(clf, CHURN_MODEL_PATH)
    joblib.dump(feature_cols, CHURN_FEATURES_PATH)
    print(f"[train_churn] Saved model to {CHURN_MODEL_PATH}")

def train_uplift():
    print("[train] Starting Uplift Training...")
    df = load_df()
    validate_and_raise(df)
    X_df, feature_cols = featurize_for_scoring(df)
    X = X_df[feature_cols].copy()
    y = df["churned"]
    t = df["treatment"]
    
    X_t = X[t == 1]; y_t = y[t == 1]
    X_c = X[t == 0]; y_c = y[t == 0]
    
    model_t = LGBMClassifier(n_estimators=50, random_state=RANDOM_STATE)
    model_c = LGBMClassifier(n_estimators=50, random_state=RANDOM_STATE)
    
    if len(X_t) < 10 or len(X_c) < 10:
        model = LGBMClassifier(n_estimators=50, random_state=RANDOM_STATE)
        model.fit(X, y)
        model_t = model_c = model
    else:
        model_t.fit(X_t, y_t)
        model_c.fit(X_c, y_c)
        
    artifacts = {"model_t": model_t, "model_c": model_c, "features": feature_cols}
    joblib.dump(artifacts, UPLIFT_PATH)
    print(f"[train_uplift] Saved uplift artifacts to {UPLIFT_PATH}")

def train_cltv():
    print("[train] Starting CLTV Training...")
    df = pd.read_csv(DATA_PATH)
    frequency = df["frequency"]
    recency = df["recency_days"]
    tenure = df["tenure_days"]
    monetary = df["monetary"]

    bgf = BetaGeoFitter(penalizer_coef=0.01)
    bgf.fit(frequency, recency, tenure)

    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(frequency, monetary)

    cltv = ggf.customer_lifetime_value(bgf, frequency, recency, tenure, monetary, time=12, freq="D", discount_rate=0.01)
    scaler = MinMaxScaler()
    scaler.fit(cltv.values.reshape(-1, 1))

    artifacts = {"bgf": bgf, "ggf": ggf, "scaler": scaler}
    joblib.dump(artifacts, CLTV_ARTIFACTS_PATH)
    print(f"[train_cltv] Saved CLTV artifacts to {CLTV_ARTIFACTS_PATH}")

def run_all_training():
    ensure_dirs([MODEL_DIR])
    train_churn()
    train_uplift()
    train_cltv()

# ----------------------------------------------------------------------------
# DECISION ENGINE & OPTIMIZER (src/decision_engine/optimizer.py)
# ----------------------------------------------------------------------------
def compute_expected_gain(df: pd.DataFrame, margin: float) -> pd.DataFrame:
    df = df.copy()
    df["expected_gain"] = df["uplift"] * df["cltv"] * margin
    df["roi"] = df["expected_gain"] / df["cost"].replace(0, 1e-9)
    return df

def roi_select(df: pd.DataFrame, budget: float, margin: float = 0.30, 
               min_profit_threshold: float = 0.0, export_csv: str = None) -> Tuple[pd.DataFrame, Dict]:
    scored = compute_expected_gain(df, margin)
    scored["net_profit"] = scored["expected_gain"] - scored["cost"]
    scored = scored[scored["net_profit"] >= min_profit_threshold]
    scored = scored.sort_values(by=["roi", "expected_gain"], ascending=[False, False])

    selected_rows = []
    spent = 0.0
    for _, r in scored.iterrows():
        cost = float(r["cost"])
        if (spent + cost) <= float(budget):
            selected_rows.append(r)
            spent += cost
        else:
            continue
            
    if not selected_rows:
        return pd.DataFrame(), {"selected_count": 0, "spent": 0.0, "expected_total_gain": 0.0}

    selected_df = pd.DataFrame(selected_rows).reset_index(drop=True)
    summary = {
        "selected_count": int(len(selected_df)),
        "spent": float(spent),
        "expected_total_gain": float(selected_df["expected_gain"].sum()),
        "avg_roi": float(selected_df["roi"].mean()),
        "avg_cost": float(selected_df["cost"].mean())
    }
    
    if export_csv:
        ensure_dirs([os.path.dirname(export_csv)])
        selected_df.to_csv(export_csv, index=False)
        
    return selected_df, summary

# ----------------------------------------------------------------------------
# REPORT GENERATOR (src/analytics/report_generator.py)
# ----------------------------------------------------------------------------
HTML_TEMPLATE = """
<html>
<head><title>Campaign Strategy Report - {campaign_name}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 30px; }}
h1 {{ color: #114b8a; }}
.kv {{ display:flex; gap:20px; }}
.kv div {{ background:#f3f6fb; padding:10px; border-radius:6px; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
th, td {{ border: 1px solid #ddd; padding: 8px; }}
th {{ background: #114b8a; color: white; }}
</style>
</head>
<body>
<h1>Campaign Strategy Report — {campaign_name}</h1>
<p>Generated: {ts}</p>
<div class="kv">
  <div><strong>Budget</strong><br/>{budget}</div>
  <div><strong>Selected Count</strong><br/>{selected_count}</div>
  <div><strong>Spent</strong><br/>{spent:.2f}</div>
  <div><strong>Expected Incremental Gain</strong><br/>{expected_total_gain:.2f}</div>
  <div><strong>Avg ROI</strong><br/>{avg_roi:.2f}</div>
</div>
<h2>Top 25 Selected Customers</h2>
{table}
</body>
</html>
"""

def generate_campaign_report(selected_df: pd.DataFrame, summary: Dict, campaign_meta: Dict, out_path: str):
    selected_count = summary.get("selected_count", 0)
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    table_html = ""
    if selected_count > 0:
        top = selected_df.head(25)[["customer_id", "uplift", "cltv", "cost", "expected_gain", "roi"]]
        table_html = top.to_html(index=False, float_format="%.4f")
    html = HTML_TEMPLATE.format(
        campaign_name=campaign_meta.get("name", "Campaign"),
        ts=ts,
        budget=campaign_meta.get("budget", 0.0),
        selected_count=selected_count,
        spent=summary.get("spent", 0.0),
        expected_total_gain=summary.get("expected_total_gain", 0.0),
        avg_roi=summary.get("avg_roi", 0.0),
        table=table_html
    )
    ensure_dirs([os.path.dirname(out_path)])
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path

# ----------------------------------------------------------------------------
# API APP (FastAPI) (src/api/main.py)
# ----------------------------------------------------------------------------
fastapi_app = FastAPI(title="DIE-Ops Customer Intelligence API")

# Add CORS Middleware
from fastapi.middleware.cors import CORSMiddleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev convenience; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model placeholders
api_models = {}

@fastapi_app.on_event("startup")
def load_models_api():
    try:
        api_models["churn_model"] = joblib.load(CHURN_MODEL_PATH)
        api_models["churn_features"] = joblib.load(CHURN_FEATURES_PATH)
        
        uplift_artifacts = joblib.load(UPLIFT_PATH)
        api_models["treat_model"] = uplift_artifacts["model_t"]
        api_models["control_model"] = uplift_artifacts["model_c"]
        api_models["uplift_features"] = uplift_artifacts["features"]
        
        cltv_artifacts = joblib.load(CLTV_ARTIFACTS_PATH)
        api_models["cltv_bgf"] = cltv_artifacts["bgf"]
        api_models["cltv_ggf"] = cltv_artifacts["ggf"]
        api_models["cltv_scaler"] = cltv_artifacts["scaler"]
        
        if os.path.exists(DATA_PATH):
            api_models["df_full"] = pd.read_csv(DATA_PATH)
        else:
            print("Warning: Data path empty, run ingest first.")
            api_models["df_full"] = pd.DataFrame()
    except Exception as e:
        print(f"Model loading failed (ignore if running ingest/train): {e}")

class CustomerScoreRequest(BaseModel):
    customer_id: int

class RecommendPayload(BaseModel):
    budget: float = 5000.0
    cost_per_action: float = 20.0
    margin: float = 0.30

def score_dataframe_api(df: pd.DataFrame):
    # Churn
    X, _ = featurize_for_scoring(df, api_models.get("churn_features"))
    if "churn_model" in api_models:
        df["churn_prob"] = api_models["churn_model"].predict_proba(X)[:, 1]
    else:
        df["churn_prob"] = 0.5
        
    # Uplift
    X_u, _ = featurize_for_scoring(df, api_models.get("uplift_features"))
    if "treat_model" in api_models:
        p_t = api_models["treat_model"].predict_proba(X_u)[:, 1]
        p_c = api_models["control_model"].predict_proba(X_u)[:, 1]
        df["uplift"] = p_t - p_c
    else:
        df["uplift"] = 0.0

    # CLTV
    if "cltv_ggf" in api_models:
        cltv_vals = api_models["cltv_ggf"].customer_lifetime_value(
            api_models["cltv_bgf"], df["frequency"], df["recency_days"], df["tenure_days"], df["monetary"],
            time=12, freq="D", discount_rate=0.01
        )
        df["cltv"] = api_models["cltv_scaler"].transform(cltv_vals.values.reshape(-1, 1))
    else:
        df["cltv"] = 0.0
    return df

@fastapi_app.post("/score/customer")
def score_customer(req: CustomerScoreRequest):
    df_full = api_models.get("df_full")
    if df_full is None or df_full.empty:
        raise HTTPException(status_code=404, detail="Data not loaded")
    
    subset = df_full[df_full["customer_id"] == req.customer_id].copy()
    if subset.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    scored = score_dataframe_api(subset)
    row = scored.iloc[0]
    return {
        "customer_id": int(row["customer_id"]),
        "churn_prob": float(row.get("churn_prob", 0)),
        "uplift": float(row.get("uplift", 0)),
        "cltv": float(row.get("cltv", 0))
    }

@fastapi_app.post("/score/batch")
def score_batch():
    df_full = api_models.get("df_full")
    if df_full is None or df_full.empty:
        raise HTTPException(status_code=500, detail="Data not available")
    
    scored = score_dataframe_api(df_full.copy())
    return scored[["customer_id", "churn_prob", "uplift", "cltv"]].to_dict(orient="records")

@fastapi_app.post("/recommend")
def recommend_api(payload: RecommendPayload):
    df_full = api_models.get("df_full")
    if df_full is None or df_full.empty:
        raise HTTPException(status_code=500, detail="Data not available")
        
    scored = score_dataframe_api(df_full.copy())
    dec = scored[["customer_id", "uplift", "cltv"]].copy()
    dec["cost"] = payload.cost_per_action
    
    selected_df, summary = roi_select(dec, budget=payload.budget, margin=payload.margin)
    return {"summary": summary, "selected_customers": selected_df.head(200).to_dict(orient="records")}

@fastapi_app.get("/simulate")
def simulate(budget: float = 5000, cost: float = 20.0, margin: float = 0.30):
    # Just an alias for simple get-based simulation
    return recommend_api(RecommendPayload(budget=budget, cost_per_action=cost, margin=margin))

@fastapi_app.get("/reports")
def list_reports():
    if not os.path.exists(OUTPUT_DIR):
        return []
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".html")]
    # return list of downloadable urls or just filenames.
    # treating output dir as static files would be best, but for now just returning names.
    return files

@fastapi_app.get("/reports/{filename}")
def get_report(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(path):
        from fastapi.responses import FileResponse
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="Report not found")

# ----------------------------------------------------------------------------
# ADMIN ENDPOINTS (for triggering ingest/train from UI)
# ----------------------------------------------------------------------------
@fastapi_app.post("/admin/ingest")
def api_ingest():
    """Trigger data ingestion from the UI."""
    try:
        run_ingest()
        return {"status": "success", "message": "Data ingestion completed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@fastapi_app.post("/admin/train")
def api_train():
    """Trigger model training from the UI."""
    try:
        run_all_training()
        # Reload models after training
        load_models_api()
        return {"status": "success", "message": "Model training completed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------------
# MAIN ENTRY POINT
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DIE-Ops Unified App")
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("ingest", help="Generate synthetic data")
    subparsers.add_parser("train", help="Train all models")
    subparsers.add_parser("api", help="Run FastAPI Backend")
    
    args = parser.parse_args()
    
    if args.command == "ingest":
        run_ingest()
    elif args.command == "train":
        run_all_training()
    elif args.command == "api":
        import uvicorn
        # Reload=True works best if running from file directly
        uvicorn.run("app:fastapi_app", host="0.0.0.0", port=8000, reload=True)
    else:
        print("Please specify a command: ingest, train, api")
