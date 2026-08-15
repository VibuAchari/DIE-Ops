from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from src.services.campaigns import CampaignRequest

router = APIRouter()

class CampaignSchema(BaseModel):
    budget: float = Field(default=5000.0, ge=0)
    margin: float = Field(default=0.30, ge=0, le=1)

@router.post("/campaign/recommend")
def recommend_campaign(payload: CampaignSchema, request: Request):
    try:
        return request.app.state.campaigns.recommend(CampaignRequest(payload.budget, payload.margin))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.get("/simulate")
def simulate(request: Request, budget: float = 5000.0, margin: float = 0.30):
    return recommend_campaign(CampaignSchema(budget=budget, margin=margin), request)
