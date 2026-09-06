"""
Demand Forecast API Endpoints
=============================
"""

from typing import Dict, Any, List
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.schemas import ForecastRequest, ForecastResponse
from backend.app.services.forecast_service import forecast_service
from backend.app.core.config import settings

router = APIRouter(prefix="/forecast", tags=["Forecasting"])


@router.post("", response_model=ForecastResponse)
def generate_forecast(req: ForecastRequest):
    """
    Generates multi-horizon forward demand predictions with confidence bounds
    for a specific Store and Product.
    """
    try:
        return forecast_service.generate_forecast(req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting engine error: {str(e)}")


@router.get("/history")
def get_historical_demand(
    store_id: str = Query(..., description="Store ID"),
    product_id: str = Query(..., description="Product SKU ID"),
    days: int = Query(default=60, ge=7, le=730, description="Historical days window"),
):
    """Returns actual historical daily demand time-series for visual charts."""
    df = pd.read_csv(settings.DATA_PATH)
    sub = df[(df["Store_ID"] == store_id) & (df["Product_ID"] == product_id)].sort_values("Date").tail(days)
    if sub.empty:
        raise HTTPException(status_code=404, detail=f"No data for Store: {store_id}, SKU: {product_id}")

    records = []
    for _, row in sub.iterrows():
        records.append({
            "date": str(row["Date"]),
            "units_sold": int(row["Units_Sold"]),
            "price": float(row["Price"]),
            "promotion": int(row["Promotion"]),
            "holiday": int(row["Holiday"]),
        })
    return {
        "store_id": store_id,
        "product_id": product_id,
        "product_name": sub["Product_Name"].iloc[0],
        "category": sub["Category"].iloc[0],
        "history": records,
    }
