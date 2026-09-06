"""
Inventory Optimization & Recommendations API Endpoints
======================================================
"""

from typing import Optional
from fastapi import APIRouter, Query
from backend.app.schemas.schemas import InventorySummaryResponse
from backend.app.services.forecast_service import forecast_service

router = APIRouter(prefix="/inventory", tags=["Inventory Optimization"])


@router.get("/status", response_model=InventorySummaryResponse)
def get_inventory_status(
    store_id: Optional[str] = Query(None, description="Filter by Store ID (e.g. STR_01)"),
):
    """
    Returns inventory levels, dynamic reorder points, safety stocks,
    recommended reorder quantities, and risk classifications across SKUs.
    """
    return forecast_service.get_inventory_summary(store_id=store_id)
