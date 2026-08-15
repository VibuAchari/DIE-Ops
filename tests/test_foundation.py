from fastapi.routing import APIRoute
import pandas as pd

from src.api.main import app
from src.services.campaigns import CampaignRequest, CampaignService


def test_application_imports_without_circular_dependency():
    assert app.title == "DIE-Ops Decision Intelligence API"


def test_expected_routes_are_registered():
    paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    assert {
        "/score/customer",
        "/policy/options/{customer_id}",
        "/policy/decision/{customer_id}",
        "/campaign/recommend",
        "/simulate",
        "/campaign/report/pdf",
    }.issubset(paths)


def test_campaign_request_validation():
    CampaignRequest(budget=100.0, margin=0.3).validate()

    try:
        CampaignRequest(budget=-1.0).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("negative budgets must be rejected")


def test_campaign_service_score_customer_with_fake_scorer():
    data = pd.DataFrame([{"customer_id": 42, "feature": 1}])

    def scorer(df):
        result = df.copy()
        result["churn_prob"] = 0.8
        result["uplift"] = 0.2
        result["cltv_raw"] = 12000
        return result

    service = CampaignService(scorer, data)
    assert service.score_customer(42) == {
        "customer_id": 42,
        "churn_prob": 0.8,
        "uplift": 0.2,
        "cltv_raw": 12000.0,
    }


def test_campaign_service_unknown_customer_raises_key_error():
    data = pd.DataFrame([{"customer_id": 42}])
    service = CampaignService(lambda df: df, data)

    try:
        service.score_customer(999)
    except KeyError:
        pass
    else:
        raise AssertionError("unknown customers must raise KeyError")
