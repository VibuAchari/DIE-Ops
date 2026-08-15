from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()

class CustomerRequest(BaseModel):
    customer_id: int

@router.post("/score/customer")
def score_customer(payload: CustomerRequest, request: Request):
    try:
        return request.app.state.campaigns.score_customer(payload.customer_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Customer not found") from exc

@router.get("/policy/options/{customer_id}")
def policy_options(customer_id: int, request: Request):
    try:
        return {"customer_id": customer_id, "options": request.app.state.campaigns.policy_options(customer_id)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Customer not found") from exc

@router.get("/policy/decision/{customer_id}")
def policy_decision(customer_id: int, request: Request):
    result = policy_options(customer_id, request)
    if not result["options"]:
        return {"customer_id": customer_id, "decision": None, "reason": "No profitable intervention available."}
    best = max(result["options"], key=lambda item: item["net_profit"])
    return {"customer_id": customer_id, "decision": {"offer": best["offer"], "cost": float(best["cost"]), "net_profit": float(best["net_profit"]), "roi_ratio": float(best["net_profit"] / best["cost"])}}
