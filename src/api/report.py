"""
src/api/report.py

Enterprise PDF Report Endpoint

Purpose:
- Generate executive-ready retention campaign reports
- Pulls directly from /campaign/recommend
- Exports locked human-readable PDF (charts + intervention rationale)

Endpoint:
✅ GET /campaign/report/pdf?budget=5000&margin=0.30
"""

import os
import tempfile
from fastapi import APIRouter
from fastapi.responses import FileResponse

from src.reporting.pdf_export import generate_campaign_pdf
from src.api.main import recommend_campaign, CampaignRequest


router = APIRouter()


# ============================================================
# Endpoint: Export Campaign Report PDF
# ============================================================
@router.get("/campaign/report/pdf")
def export_campaign_pdf(budget: float = 5000.0, margin: float = 0.30):
    """
    Generates an executive PDF report directly from campaign optimizer output.
    """

    # --------------------------------------------------------
    # 1. Run Campaign Recommendation Endpoint Internally
    # --------------------------------------------------------
    req = CampaignRequest(budget=budget, margin=margin)
    result = recommend_campaign(req)

    summary = result["summary"]
    selected_customers = result["selected_customers"]

    # --------------------------------------------------------
    # 2. Generate PDF into Temporary File
    # --------------------------------------------------------
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_path = tmp_file.name
    tmp_file.close()

    generate_campaign_pdf(
        summary=summary,
        selected_customers=selected_customers,
        output_path=pdf_path
    )

    # --------------------------------------------------------
    # 3. Return PDF as Download Response
    # --------------------------------------------------------
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="DIE_Ops_Campaign_Report.pdf"
    )
