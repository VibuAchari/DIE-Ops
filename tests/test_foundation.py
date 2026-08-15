from src.api.main import app
from src.services.campaigns import CampaignRequest


def test_application_imports_without_circular_dependency():
    assert app.title == "DIE-Ops Decision Intelligence API"


def test_campaign_request_validation():
    CampaignRequest(budget=100.0, margin=0.3).validate()

    try:
        CampaignRequest(budget=-1.0).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("negative budgets must be rejected")
