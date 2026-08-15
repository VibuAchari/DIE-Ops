"""FastAPI composition root for DIE-Ops."""
import os
from contextlib import asynccontextmanager
import joblib
import pandas as pd
from fastapi import FastAPI
from src.ingest.ingest import load_df
from src.features.featurize import featurize_for_churn, featurize_for_uplift
from src.services.campaigns import CampaignService

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(ROOT, "models")


def build_scorer():
    churn_model = joblib.load(os.path.join(MODEL_DIR, "churn_model.pkl"))
    churn_features = joblib.load(os.path.join(MODEL_DIR, "churn_features.pkl"))
    uplift = joblib.load(os.path.join(MODEL_DIR, "uplift_models.pkl"))
    cltv_table = pd.read_csv(os.path.join(MODEL_DIR, "cltv_table.csv"))

    def score(df: pd.DataFrame) -> pd.DataFrame:
        X_churn, _ = featurize_for_churn(df)
        df["churn_prob"] = churn_model.predict_proba(X_churn[churn_features])[:, 1]
        X_uplift, _ = featurize_for_uplift(df)
        p_t = uplift["model_t"].predict_proba(X_uplift)[:, 1]
        p_c = uplift["model_c"].predict_proba(X_uplift)[:, 1]
        df["uplift"] = p_c - p_t
        df = df.merge(cltv_table[["customer_id", "cltv_raw"]], on="customer_id", how="left")
        if df["cltv_raw"].isna().any():
            raise RuntimeError("Missing CLTV values for scored customers")
        return df

    return score


@asynccontextmanager
async def lifespan(app: FastAPI):
    df = load_df()
    app.state.campaigns = CampaignService(build_scorer(), df)
    yield


app = FastAPI(title="DIE-Ops Decision Intelligence API", lifespan=lifespan)

from src.api.routes.campaigns import router as campaign_router
from src.api.routes.reports import router as report_router
from src.api.routes.scoring import router as scoring_router

app.include_router(scoring_router)
app.include_router(campaign_router)
app.include_router(report_router)
