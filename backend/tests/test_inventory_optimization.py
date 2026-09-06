"""
Unit Tests for Inventory Optimization & Risk Classification
============================================================
"""

import pytest
from ml.inference.risk_classifier import RiskClassifier, InventoryRiskStatus
from ml.inference.optimizer import InventoryOptimizer, get_z_score


def test_z_score_lookup():
    """Validates Z-score critical values for standard service levels."""
    assert round(get_z_score(0.95), 3) == 1.645
    assert round(get_z_score(0.99), 3) == 2.326
    assert round(get_z_score(0.90), 3) == 1.282


def test_safety_stock_and_rop_calculation():
    """Validates mathematical safety stock and reorder point formulas."""
    optimizer = InventoryOptimizer(default_service_level=0.95, default_lead_time_days=4)

    # 4 days of forecast demand = 25 units/day -> LTD = 100
    # demand std = 10, L = 4, sqrt(L) = 2, Z = 1.645
    # SS = ceil(1.645 * 10 * 2) = ceil(32.9) = 33
    # ROP = LTD + SS = 100 + 33 = 133
    res = optimizer.optimize_sku(
        product_id="PRD_01",
        product_name="Milk",
        category="Dairy",
        store_id="STR_01",
        current_stock=100,  # Below ROP (133)
        forecast_daily_demands=[25.0, 25.0, 25.0, 25.0],
        historical_demand_std=10.0,
        lead_time_days=4,
        service_level=0.95,
        review_period_days=4,
    )

    assert res["safety_stock"] == 33
    assert res["reorder_point"] == 133
    assert res["lead_time_demand"] == 100.0
    # Current stock (100) <= ROP (133) -> Reorder triggered
    assert res["recommended_reorder_qty"] > 0
    assert res["risk_status"] == "LOW_STOCK"


def test_risk_classification_tiers():
    """Validates all 4 risk classification states and explanations."""
    # 1. Stockout risk: Current stock < LTD
    status, reason = RiskClassifier.classify(current_stock=20, lead_time_demand=50.0, reorder_point=70, target_inventory=150)
    assert status == InventoryRiskStatus.STOCKOUT_RISK
    assert "CRITICAL" in reason

    # 2. Low Stock: LTD <= Current stock <= ROP
    status, reason = RiskClassifier.classify(current_stock=60, lead_time_demand=50.0, reorder_point=70, target_inventory=150)
    assert status == InventoryRiskStatus.LOW_STOCK
    assert "REORDER RECOMMENDED" in reason

    # 3. Healthy: ROP < Current stock <= Target * 1.4
    status, reason = RiskClassifier.classify(current_stock=100, lead_time_demand=50.0, reorder_point=70, target_inventory=150)
    assert status == InventoryRiskStatus.HEALTHY
    assert "HEALTHY" in reason

    # 4. Overstock Risk: Current stock > Target * 1.4
    status, reason = RiskClassifier.classify(current_stock=250, lead_time_demand=50.0, reorder_point=70, target_inventory=150)
    assert status == InventoryRiskStatus.OVERSTOCK_RISK
    assert "OVERSTOCK" in reason
