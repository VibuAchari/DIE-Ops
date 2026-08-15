"""Customer scoring and policy HTTP routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.dependencies import get_campaign_service
from src.services.campaigns import CampaignService

router = APIRouter()


class CustomerRequest(BaseModel):
    customer_id: int


@router.post("/score/customer")
def score_customer(
    payload: CustomerRequest,
    service: CampaignService = Depends(get_campaign_service),
):
    try:
        return service.score_customer(payload.customer_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Customer not found") from exc


@router.get("/policy/options/{customer_id}")
def policy_options(
    customer_id: int,
    service: CampaignService = Depends(get_campaign_service),
):
    try:
        return {
            "customer_id": customer_id,
            "options": service.policy_options(customer_id),
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Customer not found") from exc


@router.get("/policy/decision/{customer_id}")
def policy_decision(
    customer_id: int,
    service: CampaignService = Depends(get_campaign_service),
):
    try:
        return service.policy_decision(customer_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Customer not found") from exc
