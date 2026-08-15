"""Campaign HTTP routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.api.dependencies import get_campaign_service
from src.services.campaigns import CampaignRequest, CampaignService

router = APIRouter()


class CampaignSchema(BaseModel):
    budget: float = Field(default=5000.0, ge=0)
    margin: float = Field(default=0.30, ge=0, le=1)


@router.post("/campaign/recommend")
def recommend_campaign(
    payload: CampaignSchema,
    service: CampaignService = Depends(get_campaign_service),
):
    try:
        request = CampaignRequest(budget=payload.budget, margin=payload.margin)
        return service.recommend(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/simulate")
def simulate(
    budget: float = 5000.0,
    margin: float = 0.30,
    service: CampaignService = Depends(get_campaign_service),
):
    try:
        return service.recommend(CampaignRequest(budget=budget, margin=margin))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
