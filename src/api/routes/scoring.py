from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()

class CustomerRequest(BaseModel):
    customer_id: int

@router.post("/score/customer")
def score_customer(payload: CustomerRequest, request: Request):
    service = request.app.state.campaigns
    df = service._customer_data[service._customer_data["customer_id"] == payload.customer_id].copy()
    if df.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    scored = service._scorer(df)
    row = scored.iloc[0]
    return {
        "customer_id": int(row["customer_id"]),
        "churn_prob": float(row["churn_prob"]),
        "uplift": float(row["uplift"]),
        "cltv_raw": float(row["cltv_raw"]),
    }

@router.get("/policy/options/{customer_id}")
def policy_options(customer_id: int, request: Request):
    from src.decision_engine.actions import build_action_candidates
    service = request.app.state.campaigns
    df = service._customer_data[service._customer_data["customer_id"] == customer_id].copy()
    if df.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    candidates = build_action_candidates(service._scorer(df), margin=0.30)
    return {"customer_id": customer_id, "options": candidates.to_dict(orient="records")}

@router.get("/policy/decision/{customer_id}")
def policy_decision(customer_id: int, request: Request):
    result = policy_options(customer_id, request)
    if not result["options"]:
        return {"customer_id": customer_id, "decision": None, "reason": "No profitable intervention available."}
    best = max(result["options"], key=lambda item: item["net_profit"])
    return {"customer_id": customer_id, "decision": {"offer": best["offer"], "cost": float(best["cost"]), "net_profit": float(best["net_profit"]), "roi_ratio": float(best["net_profit"] / best["cost"])}}
