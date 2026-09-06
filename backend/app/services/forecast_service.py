"""
Demand Forecasting & Inventory Service
======================================
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.entities import Product, Store, Inventory, Sale
from backend.app.schemas.schemas import (
    ForecastRequest,
    ForecastResponse,
    DailyForecastItem,
    InventoryStatusItem,
    InventorySummaryResponse,
)
from ml.inference.forecaster import MultiHorizonForecaster
from ml.inference.optimizer import InventoryOptimizer
from ml.inference.scenario_simulator import ScenarioSimulator


class ForecastService:
    """Provides demand prediction and inventory optimization services."""

    def __init__(self):
        self.forecaster = MultiHorizonForecaster(registry_dir=settings.MODEL_REGISTRY_PATH)
        self.optimizer = InventoryOptimizer()
        self.simulator = ScenarioSimulator(forecaster=self.forecaster, optimizer=self.optimizer)
        self._df_cache: Optional[pd.DataFrame] = None

    def _get_historical_df(self) -> pd.DataFrame:
        if self._df_cache is None or os.path.exists(settings.DATA_PATH):
            self._df_cache = pd.read_csv(settings.DATA_PATH)
        return self._df_cache

    def generate_forecast(self, req: ForecastRequest) -> ForecastResponse:
        df = self._get_historical_df()

        sku_sub = df[(df["Store_ID"] == req.store_id) & (df["Product_ID"] == req.product_id)]
        if sku_sub.empty:
            raise ValueError(f"Store '{req.store_id}' with Product '{req.product_id}' not found.")

        product_name = sku_sub["Product_Name"].iloc[0]
        category = sku_sub["Category"].iloc[0]

        overrides = {
            "demand_growth_pct": req.demand_growth_pct,
            "price_change_pct": req.price_change_pct,
            "is_promotion": req.is_promotion,
        }

        forecast_df = self.forecaster.forecast(
            historical_df=df,
            store_id=req.store_id,
            product_id=req.product_id,
            horizon_days=req.horizon_days,
            scenario_overrides=overrides,
        )

        daily_items = []
        for _, row in forecast_df.iterrows():
            daily_items.append(
                DailyForecastItem(
                    date=row["Date"],
                    day_of_week=row["Day_of_Week"],
                    predicted_demand=float(row["Predicted_Demand"]),
                    lower_bound=float(row["Lower_Bound"]),
                    upper_bound=float(row["Upper_Bound"]),
                    promotion=int(row["Promotion"]),
                    price=float(row["Price"]),
                )
            )

        total_demand = sum([d.predicted_demand for d in daily_items])
        avg_demand = round(total_demand / len(daily_items), 2) if daily_items else 0.0

        return ForecastResponse(
            store_id=req.store_id,
            product_id=req.product_id,
            product_name=product_name,
            category=category,
            horizon_days=req.horizon_days,
            model_used=self.forecaster.metadata.get("model_name", "LightGBM"),
            total_forecast_demand=round(total_demand, 1),
            avg_daily_demand=avg_demand,
            daily_forecasts=daily_items,
        )

    def get_inventory_summary(self, store_id: Optional[str] = None) -> InventorySummaryResponse:
        df = self._get_historical_df()
        latest_date = df["Date"].max()
        snapshot = df[df["Date"] == latest_date].copy()

        if store_id:
            snapshot = snapshot[snapshot["Store_ID"] == store_id]

        items: List[InventoryStatusItem] = []
        stockout_count = 0
        low_stock_count = 0
        healthy_count = 0
        overstock_count = 0
        total_reorder_units = 0

        for _, row in snapshot.iterrows():
            s_id = row["Store_ID"]
            p_id = row["Product_ID"]
            curr_stock = int(row["Inventory_Level"])

            sku_hist = df[(df["Store_ID"] == s_id) & (df["Product_ID"] == p_id)]
            hist_std = float(sku_hist["Units_Sold"].std()) if len(sku_hist) > 1 else 5.0

            forecast_df = self.forecaster.forecast(df, store_id=s_id, product_id=p_id, horizon_days=14)
            demands = forecast_df["Predicted_Demand"].tolist()

            opt = self.optimizer.optimize_sku(
                product_id=p_id,
                product_name=row["Product_Name"],
                category=row["Category"],
                store_id=s_id,
                current_stock=curr_stock,
                forecast_daily_demands=demands,
                historical_demand_std=hist_std,
                lead_time_days=5,
                service_level=0.95,
            )

            status = opt["risk_status"]
            if status == "STOCKOUT_RISK":
                stockout_count += 1
            elif status == "LOW_STOCK":
                low_stock_count += 1
            elif status == "OVERSTOCK_RISK":
                overstock_count += 1
            else:
                healthy_count += 1

            total_reorder_units += opt["recommended_reorder_qty"]
            items.append(InventoryStatusItem(**opt))

        return InventorySummaryResponse(
            total_products_tracked=len(items),
            total_inventory_units=int(snapshot["Inventory_Level"].sum()),
            stockout_risk_count=stockout_count,
            low_stock_count=low_stock_count,
            healthy_count=healthy_count,
            overstock_risk_count=overstock_count,
            total_recommended_reorder_units=total_reorder_units,
            items=items,
        )


forecast_service = ForecastService()
