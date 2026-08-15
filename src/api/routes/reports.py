"""Campaign report HTTP route."""

import os
import tempfile

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import FileResponse

from src.api.dependencies import get_campaign_service
from src.reporting.pdf_export import generate_campaign_pdf
from src.services.campaigns import CampaignRequest, CampaignService

router = APIRouter()


def _remove_file(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


@router.get("/campaign/report/pdf")
def export_campaign_pdf(
    background_tasks: BackgroundTasks,
    budget: float = 5000.0,
    margin: float = 0.30,
    service: CampaignService = Depends(get_campaign_service),
):
    result = service.recommend(CampaignRequest(budget=budget, margin=margin))
    fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        generate_campaign_pdf(
            summary=result["summary"],
            customers=result["selected_customers"],
            output_file=pdf_path,
        )
    except Exception:
        _remove_file(pdf_path)
        raise

    background_tasks.add_task(_remove_file, pdf_path)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="DIE_Ops_Campaign_Report.pdf",
        background=background_tasks,
    )
