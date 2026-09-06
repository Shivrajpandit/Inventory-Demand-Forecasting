"""
What-If Scenario Simulation API Endpoints
=========================================
"""

import uuid
from typing import Dict, Any, List
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.entities import Scenario
from backend.app.schemas.schemas import ScenarioSimulationRequest, ScenarioSaveRequest
from backend.app.services.forecast_service import forecast_service
from backend.app.core.config import settings

router = APIRouter(prefix="/scenario", tags=["What-If Scenarios"])


@router.post("/simulate")
def run_scenario_simulation(req: ScenarioSimulationRequest):
    """
    Simulates demand growth, price elasticity, lead time changes, and target service level shifts.
    """
    df = pd.read_csv(settings.DATA_PATH)

    # If current stock not provided, pull latest snapshot
    current_stock = req.current_stock
    if current_stock is None:
        latest = df[(df["Store_ID"] == req.store_id) & (df["Product_ID"] == req.product_id)]
        current_stock = int(latest["Inventory_Level"].iloc[-1]) if not latest.empty else 100

    scenario_params = {
        "demand_growth_pct": req.demand_growth_pct,
        "price_change_pct": req.price_change_pct,
        "lead_time_days": req.lead_time_days or 7,
        "service_level": req.service_level or 0.95,
        "is_promotion": req.is_promotion,
    }

    try:
        res = forecast_service.simulator.simulate(
            historical_df=df,
            store_id=req.store_id,
            product_id=req.product_id,
            current_stock=current_stock,
            scenario_params=scenario_params,
            horizon_days=req.horizon_days,
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@router.post("/save")
def save_scenario(req: ScenarioSaveRequest, db: Session = Depends(get_db)):
    sc = Scenario(
        name=req.name,
        store_id=req.store_id,
        product_id=req.product_id,
        input_parameters=req.input_parameters,
        simulation_results=req.simulation_results,
    )
    db.add(sc)
    db.commit()
    db.refresh(sc)
    return {"id": sc.id, "message": "Scenario saved successfully."}


@router.get("/saved")
def list_saved_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(Scenario).order_by(Scenario.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "store_id": s.store_id,
            "product_id": s.product_id,
            "input_parameters": s.input_parameters,
            "simulation_results": s.simulation_results,
            "created_at": s.created_at.isoformat(),
        }
        for s in scenarios
    ]
