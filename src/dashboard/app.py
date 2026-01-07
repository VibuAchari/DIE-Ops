"""
src/dashboard/app.py
Streamlit dashboard skeleton that:
 - shows KPIs
 - allows uploading a small CSV or uses sample dataset
 - calls local API endpoints to score/recommend
 - provides a simple simulator UI

Run: `streamlit run src/dashboard/app.py`
"""
import streamlit as st
import pandas as pd
import requests
import os
import json

API_URL = "http://localhost:8000"

st.set_page_config(page_title="DIE-Ops: Customer Intelligence", layout="wide")

st.title("DIE-Ops: Customer Intelligence (MVP)")

@st.cache_data
def load_sample():
    csv = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_customers.csv")
    if os.path.exists(csv):
        return pd.read_csv(csv)
    else:
        # if missing, call API to ensure dataset exists
        try:
            resp = requests.get(API_URL + "/simulate")
            # on first run, sample will be created by training scripts
        except Exception:
            pass
        if os.path.exists(csv):
            return pd.read_csv(csv)
        else:
            st.error("Sample data missing. Run `python src/ingest/ingest.py` to generate data.")
            return pd.DataFrame()

df = load_sample()
if df.empty:
    st.stop()

# KPIs
st.header("Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Customers", int(len(df)))
col2.metric("Avg Frequency", round(df["frequency"].mean(), 2))
col3.metric("Avg Monetary", round(df["monetary"].mean(), 2))

# Customer list and score button
st.header("Score a sample of customers")
sample = df.sample(min(50, len(df)))
st.dataframe(sample[["customer_id", "recency_days", "frequency", "monetary"]].head(20))

if st.button("Run Simulation (server-side)"):
    try:
        r = requests.get(API_URL + "/simulate")
        st.write("Simulation result:", r.json())
    except Exception as e:
        st.error(f"Failed to call API: {e}")

# Campaign builder
st.header("Campaign Builder")
budget = st.number_input("Budget (₹)", value=5000.0, step=500.0)
cost_per_action = st.number_input("Cost per action (₹)", value=50.0, step=10.0)
if st.button("Build campaign using sample customers"):
    # build payload
    customers = []
    for _, row in df.sample(min(200, len(df))).iterrows():
        customers.append({
            "customer_id": row["customer_id"],
            "recency_days": int(row["recency_days"]),
            "frequency": int(row["frequency"]),
            "monetary": float(row["monetary"]),
            "tenure_days": int(row["tenure_days"]),
            "last_purchase_amount": float(row["last_purchase_amount"]),
            "treatment": int(row.get("treatment", 0))
        })
    payload = {"customers": customers, "budget": float(budget), "cost_per_action": float(cost_per_action)}
    try:
        r = requests.post(API_URL + "/recommend", json=payload, timeout=60)
        res = r.json()
        st.write("Campaign Summary:", res.get("summary"))
        st.dataframe(pd.DataFrame(res.get("selected_customers")))
    except Exception as e:
        st.error(f"API call failed: {e}")

st.markdown("---")
st.caption("MVP dashboard: minimal, functional, and designed for demos. Extend UI as needed.")
