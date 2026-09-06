"""
Unit Tests for What-If Scenario Analysis Simulator
==================================================
"""

import pytest
import pandas as pd
import numpy as np
from ml.inference.scenario_simulator import ScenarioSimulator


def test_scenario_simulator_demand_growth():
    """Validates that +20% demand growth scales future demand and expands safety stock / ROP."""
    df = pd.read_csv("data/processed/cleaned_sales_data.csv")
    simulator = ScenarioSimulator()

    sim = simulator.simulate(
        historical_df=df,
        store_id="STR_01",
        product_id="PRD_01",
        current_stock=100,
        scenario_params={
            "demand_growth_pct": 20.0,
            "service_level": 0.99,
            "lead_time_days": 7,
        },
        horizon_days=7,
    )

    comp = sim["comparison"]
    assert comp["total_forecast_demand"]["scenario"] > comp["total_forecast_demand"]["baseline"]
    assert comp["safety_stock"]["scenario"] >= comp["safety_stock"]["baseline"]
    assert comp["reorder_point"]["scenario"] > comp["reorder_point"]["baseline"]
    assert len(sim["daily_forecast_curves"]["dates"]) == 7
