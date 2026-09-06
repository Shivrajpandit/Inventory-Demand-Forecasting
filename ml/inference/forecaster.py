"""
Multi-Horizon Demand Forecaster
===============================
Performs recursive multi-step future demand forecasting using the Champion model
and dynamic feature updates.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from ml.forecasting.registry import ModelRegistry
from ml.features.feature_pipeline import FeaturePipeline


class MultiHorizonForecaster:
    """Generates multi-day future demand point forecasts and uncertainty bands."""

    def __init__(self, registry_dir: str = "models"):
        self.registry = ModelRegistry(registry_dir=registry_dir)
        self.model = self.registry.load_champion_model()
        self.metadata = self.registry.load_champion_metadata()
        self.pipeline = FeaturePipeline()

    def forecast(
        self,
        historical_df: pd.DataFrame,
        store_id: str,
        product_id: str,
        horizon_days: int = 14,
        scenario_overrides: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        Recursively forecasts demand for the given Store and SKU over horizon_days.

        Args:
            historical_df: Cleaned historical sales records.
            store_id: Target Store ID.
            product_id: Target Product SKU ID.
            horizon_days: Number of future days to predict (e.g., 7, 14, 30).
            scenario_overrides: Optional simulation modifiers (growth %, price delta, promo).

        Returns:
            DataFrame containing future dates, predicted units, and uncertainty bounds.
        """
        scenario_overrides = scenario_overrides or {}
        growth_multiplier = 1.0 + (scenario_overrides.get("demand_growth_pct", 0.0) / 100.0)
        price_delta_pct = scenario_overrides.get("price_change_pct", 0.0)
        override_promo = scenario_overrides.get("is_promotion", None)

        # Filter SKU history
        sku_df = (
            historical_df[(historical_df["Store_ID"] == store_id) & (historical_df["Product_ID"] == product_id)]
            .sort_values("Date")
            .copy()
        )
        if sku_df.empty:
            raise ValueError(f"No historical records found for Store: {store_id}, SKU: {product_id}")

        product_name = sku_df["Product_Name"].iloc[0]
        category = sku_df["Category"].iloc[0]
        base_price = sku_df["Price"].iloc[-1]
        sim_price = round(base_price * (1.0 + (price_delta_pct / 100.0)), 2)

        last_date = pd.to_datetime(sku_df["Date"].max())
        history_buffer = sku_df.copy()
        history_buffer["Date"] = pd.to_datetime(history_buffer["Date"])

        future_rows = []

        # Model residual standard deviation for confidence intervals
        rmse = self.metadata.get("metrics", {}).get("RMSE", 5.0)

        for step in range(1, horizon_days + 1):
            next_date = last_date + timedelta(days=step)
            dow = next_date.weekday()
            month = next_date.month

            # Determine promo & discount
            if override_promo is not None:
                is_promo = int(override_promo)
            else:
                is_promo = 1 if dow in [4, 5] and step % 7 == 0 else 0
            discount = 0.15 if is_promo else 0.0

            # Generate candidate row
            new_row = {
                "Date": next_date,
                "Store_ID": store_id,
                "Product_ID": product_id,
                "Product_Name": product_name,
                "Category": category,
                "Units_Sold": 0.0,  # placeholder
                "Price": sim_price,
                "Discount": discount,
                "Promotion": is_promo,
                "Holiday": 0,
                "Day_of_Week": dow,
                "Month": month,
                "Season": "Summer" if month in [6, 7, 8] else "Winter",
                "Inventory_Level": 100.0,
            }

            temp_df = pd.concat([history_buffer, pd.DataFrame([new_row])], ignore_index=True)
            temp_feat = self.pipeline.transform(temp_df, drop_na=False)

            # Predict on the last row
            pred_row = temp_feat.iloc[-1:]
            pred_val = float(self.model.predict(pred_row)[0])
            # Apply scenario growth
            pred_val = max(0.0, round(pred_val * growth_multiplier, 2))

            # Uncertainty bounds (95% CI: +/- 1.96 * RMSE * sqrt(step_decay))
            step_uncertainty = 1.96 * rmse * (1.0 + 0.05 * np.sqrt(step))
            lower_bound = max(0.0, round(pred_val - step_uncertainty, 2))
            upper_bound = round(pred_val + step_uncertainty, 2)

            future_rows.append({
                "Date": next_date.strftime("%Y-%m-%d"),
                "Day_of_Week": next_date.strftime("%a"),
                "Predicted_Demand": pred_val,
                "Lower_Bound": lower_bound,
                "Upper_Bound": upper_bound,
                "Promotion": is_promo,
                "Price": sim_price,
            })

            # Update history buffer for autoregressive lag chaining
            new_row["Units_Sold"] = pred_val
            history_buffer = pd.concat([history_buffer, pd.DataFrame([new_row])], ignore_index=True)

        return pd.DataFrame(future_rows)
