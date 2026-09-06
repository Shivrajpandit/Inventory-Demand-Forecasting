"""
End-to-End User Lifecycle & Workflow Integration Test
=====================================================
Validates the complete workflow:
Raw Ingestion -> Cleaning -> Feature Store -> ML Inference ->
Inventory Optimization -> What-If Sandbox -> REST API Dashboard.
"""

import os
import pytest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient

from backend.app.main import app
from ml.preprocessing.ingestion import DataIngestion
from ml.preprocessing.cleaner import DataCleaner
from ml.features.feature_pipeline import FeaturePipeline
from ml.inference.forecaster import MultiHorizonForecaster
from ml.inference.optimizer import InventoryOptimizer
from ml.inference.scenario_simulator import ScenarioSimulator


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_complete_end_to_end_pipeline_workflow(client):
    """
    Tests the complete end-to-end data science and inventory optimization pipeline.
    """
    data_path = "data/raw/sales_data.csv"
    assert os.path.exists(data_path), "Raw dataset must exist."

    # 1. Ingestion & Validation
    ingestion = DataIngestion()
    raw_df, report = ingestion.ingest_csv(data_path, validate=True)
    assert report.is_valid is True
    assert report.total_rows > 0

    # 2. Cleaning & Time Grid
    cleaner = DataCleaner()
    clean_df = cleaner.clean(raw_df)
    assert len(clean_df) >= len(raw_df)
    assert (clean_df["Units_Sold"] >= 0).all()

    # 3. Feature Pipeline
    pipeline = FeaturePipeline()
    feat_df = pipeline.transform(clean_df, drop_na=True)
    assert "Lag_1" in feat_df.columns
    assert "Rolling_Mean_7" in feat_df.columns

    # 4. Multi-Horizon Forecasting
    forecaster = MultiHorizonForecaster(registry_dir="models")
    f_df = forecaster.forecast(
        historical_df=clean_df,
        store_id="STR_01",
        product_id="PRD_01",
        horizon_days=14,
    )
    assert len(f_df) == 14
    demands = f_df["Predicted_Demand"].tolist()
    assert all(d >= 0 for d in demands)

    # 5. Inventory Replenishment Optimization
    optimizer = InventoryOptimizer(default_service_level=0.95, default_lead_time_days=5)
    opt = optimizer.optimize_sku(
        product_id="PRD_01",
        product_name="Organic Whole Milk 1 Gal",
        category="Dairy",
        store_id="STR_01",
        current_stock=150,
        forecast_daily_demands=demands,
        historical_demand_std=12.0,
    )
    assert opt["safety_stock"] > 0
    assert opt["reorder_point"] > opt["safety_stock"]
    assert opt["risk_status"] in ["HEALTHY", "LOW_STOCK", "STOCKOUT_RISK", "OVERSTOCK_RISK"]

    # 6. What-If Scenario Simulation
    simulator = ScenarioSimulator(forecaster=forecaster, optimizer=optimizer)
    sim = simulator.simulate(
        historical_df=clean_df,
        store_id="STR_01",
        product_id="PRD_01",
        current_stock=150,
        scenario_params={
            "demand_growth_pct": 30.0,
            "service_level": 0.99,
            "lead_time_days": 7,
        },
        horizon_days=14,
    )
    assert sim["comparison"]["total_forecast_demand"]["scenario"] > sim["comparison"]["total_forecast_demand"]["baseline"]

    # 7. Verify via REST API
    dash_res = client.get("/api/dashboard/summary")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_sales_volume"] > 0
    assert dash_data["champion_model_name"] != ""
