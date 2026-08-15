import os
import tempfile
from fastapi import APIRouter, Request
from fastapi.background import BackgroundTasks
from fastapi.responses import FileResponse
from src.reporting.pdf_export import generate_campaign_pdf
from src.services.campaigns import CampaignRequest

router = APIRouter()

def _remove_file(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

@router.get("/campaign/report/pdf")
def export_campaign_pdf(request: Request, background_tasks: BackgroundTasks, budget: float = 5000.0, margin: float = 0.30):
    result = request.app.state.campaigns.recommend(CampaignRequest(budget=budget, margin=margin))
    fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    generate_campaign_pdf(summary=result["summary"], customers=result["selected_customers"], output_file=pdf_path)
    background_tasks.add_task(_remove_file, pdf_path)
    return FileResponse(pdf_path, media_type="application/pdf", filename="DIE_Ops_Campaign_Report.pdf", background=background_tasks)
