"""
What-If Scenario Simulation Engine
==================================
Simulates demand shifts, pricing changes, lead time disruptions, and service level targets,
comparing baseline replenishment policies with scenario requirements.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

from ml.inference.forecaster import MultiHorizonForecaster
from ml.inference.optimizer import InventoryOptimizer


class ScenarioSimulator:
    """Executes what-if simulations on demand, price elasticity, and supply chain lead times."""

    def __init__(
        self,
        forecaster: Optional[MultiHorizonForecaster] = None,
        optimizer: Optional[InventoryOptimizer] = None,
    ):
        self.forecaster = forecaster or MultiHorizonForecaster()
        self.optimizer = optimizer or InventoryOptimizer()

    def simulate(
        self,
        historical_df: pd.DataFrame,
        store_id: str,
        product_id: str,
        current_stock: int,
        scenario_params: Dict[str, Any],
        horizon_days: int = 14,
    ) -> Dict[str, Any]:
        """
        Runs both baseline and scenario simulations for comparison.

        Scenario parameters supported:
        - demand_growth_pct: float (e.g., +20.0 for +20% demand)
        - price_change_pct: float (e.g., -10.0 for 10% price cut)
        - lead_time_days: int (e.g., 10 instead of 7)
        - service_level: float (e.g., 0.99 instead of 0.95)
        - is_promotion: bool (override promotion state)
        """
        # 1. Historical SKU stats
        sku_df = historical_df[(historical_df["Store_ID"] == store_id) & (historical_df["Product_ID"] == product_id)]
        if sku_df.empty:
            raise ValueError(f"No records found for Store: {store_id}, Product: {product_id}")

        product_name = sku_df["Product_Name"].iloc[0]
        category = sku_df["Category"].iloc[0]
        hist_std = float(sku_df["Units_Sold"].std()) if len(sku_df) > 1 else 5.0
        base_lead_time = int(scenario_params.get("base_lead_time_days", 7))
        sim_lead_time = int(scenario_params.get("lead_time_days", base_lead_time))

        base_service_level = 0.95
        sim_service_level = float(scenario_params.get("service_level", base_service_level))

        # 2. Run Baseline Forecast (No overrides)
        base_forecast_df = self.forecaster.forecast(
            historical_df=historical_df,
            store_id=store_id,
            product_id=product_id,
            horizon_days=horizon_days,
            scenario_overrides={},
        )
        base_demands = base_forecast_df["Predicted_Demand"].tolist()

        # 3. Run Scenario Forecast (With overrides)
        sim_forecast_df = self.forecaster.forecast(
            historical_df=historical_df,
            store_id=store_id,
            product_id=product_id,
            horizon_days=horizon_days,
            scenario_overrides=scenario_params,
        )
        sim_demands = sim_forecast_df["Predicted_Demand"].tolist()

        # 4. Baseline Inventory Optimization
        base_opt = self.optimizer.optimize_sku(
            product_id=product_id,
            product_name=product_name,
            category=category,
            store_id=store_id,
            current_stock=current_stock,
            forecast_daily_demands=base_demands,
            historical_demand_std=hist_std,
            lead_time_days=base_lead_time,
            service_level=base_service_level,
        )

        # 5. Scenario Inventory Optimization
        sim_opt = self.optimizer.optimize_sku(
            product_id=product_id,
            product_name=product_name,
            category=category,
            store_id=store_id,
            current_stock=current_stock,
            forecast_daily_demands=sim_demands,
            historical_demand_std=hist_std,
            lead_time_days=sim_lead_time,
            service_level=sim_service_level,
        )

        # 6. Compute deltas & impact
        total_base_demand = sum(base_demands)
        total_sim_demand = sum(sim_demands)
        demand_delta_pct = round(((total_sim_demand - total_base_demand) / total_base_demand) * 100, 2) if total_base_demand > 0 else 0.0

        reorder_qty_delta = sim_opt["recommended_reorder_qty"] - base_opt["recommended_reorder_qty"]
        safety_stock_delta = sim_opt["safety_stock"] - base_opt["safety_stock"]

        return {
            "store_id": store_id,
            "product_id": product_id,
            "product_name": product_name,
            "scenario_parameters": scenario_params,
            "comparison": {
                "total_forecast_demand": {
                    "baseline": round(total_base_demand, 1),
                    "scenario": round(total_sim_demand, 1),
                    "delta_percentage": demand_delta_pct,
                },
                "safety_stock": {
                    "baseline": base_opt["safety_stock"],
                    "scenario": sim_opt["safety_stock"],
                    "delta_units": safety_stock_delta,
                },
                "reorder_point": {
                    "baseline": base_opt["reorder_point"],
                    "scenario": sim_opt["reorder_point"],
                    "delta_units": sim_opt["reorder_point"] - base_opt["reorder_point"],
                },
                "recommended_order_qty": {
                    "baseline": base_opt["recommended_reorder_qty"],
                    "scenario": sim_opt["recommended_reorder_qty"],
                    "delta_units": reorder_qty_delta,
                },
                "risk_status": {
                    "baseline": base_opt["risk_status"],
                    "scenario": sim_opt["risk_status"],
                },
            },
            "daily_forecast_curves": {
                "dates": base_forecast_df["Date"].tolist(),
                "baseline_demand": base_demands,
                "scenario_demand": sim_demands,
            },
        }
