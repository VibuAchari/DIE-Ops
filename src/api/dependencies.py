"""FastAPI dependency providers for application services."""

from fastapi import Request

from src.services.campaigns import CampaignService


def get_campaign_service(request: Request) -> CampaignService:
    """Return the application campaign service from the composition container."""
    return request.app.state.campaigns
