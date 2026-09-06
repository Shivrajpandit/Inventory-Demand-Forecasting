"""
Dashboard Analytics API Endpoints
=================================
"""

from fastapi import APIRouter
from backend.app.schemas.schemas import DashboardSummaryResponse
from backend.app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary():
    """Returns top executive KPI cards, sales volume, category distributions, and model health."""
    return dashboard_service.get_summary()
