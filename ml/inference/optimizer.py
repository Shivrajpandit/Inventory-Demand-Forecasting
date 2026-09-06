"""
Inventory Optimization Engine
=============================
Computes mathematical safety stock, dynamic reorder points, economic reorder quantities,
and stock risk classifications grounded in inventory control theory.
"""

from typing import Dict, Any, Optional, List
import math
import numpy as np
import pandas as pd

from ml.inference.risk_classifier import RiskClassifier, InventoryRiskStatus


# Standard Normal Z-Score Lookup for Service Levels
SERVICE_LEVEL_Z_MAP = {
    0.80: 0.842,
    0.85: 1.036,
    0.90: 1.282,
    0.95: 1.645,
    0.98: 2.054,
    0.99: 2.326,
    0.999: 3.090,
}


def get_z_score(service_level: float) -> float:
    """Returns standard normal critical value Z for target non-stockout probability."""
    # Find closest mapped key
    closest_sl = min(SERVICE_LEVEL_Z_MAP.keys(), key=lambda k: abs(k - service_level))
    return SERVICE_LEVEL_Z_MAP[closest_sl]


class InventoryOptimizer:
    """Calculates inventory replenishment policies from ML demand forecasts and SKU constraints."""

    def __init__(
        self,
        default_service_level: float = 0.95,
        default_lead_time_days: int = 7,
        default_review_period_days: int = 7,
    ):
        self.default_service_level = default_service_level
        self.default_lead_time_days = default_lead_time_days
        self.default_review_period_days = default_review_period_days

    def optimize_sku(
        self,
        product_id: str,
        product_name: str,
        category: str,
        store_id: str,
        current_stock: int,
        forecast_daily_demands: List[float],
        historical_demand_std: float,
        lead_time_days: Optional[int] = None,
        service_level: Optional[float] = None,
        review_period_days: Optional[int] = None,
        min_order_qty: int = 1,
        pack_size: int = 1,
        stock_on_order: int = 0,
    ) -> Dict[str, Any]:
        """
        Computes dynamic inventory optimization metrics and actionable reorder recommendation.
        """
        L = lead_time_days if lead_time_days is not None else self.default_lead_time_days
        SL = service_level if service_level is not None else self.default_service_level
        R = review_period_days if review_period_days is not None else self.default_review_period_days

        z_score = get_z_score(SL)

        # 1. Lead Time Demand (sum over lead time horizon)
        if len(forecast_daily_demands) >= L:
            lead_time_demand = float(np.sum(forecast_daily_demands[:L]))
            avg_daily_demand = float(np.mean(forecast_daily_demands[:L]))
        else:
            avg_daily_demand = float(np.mean(forecast_daily_demands)) if forecast_daily_demands else 10.0
            lead_time_demand = float(avg_daily_demand * L)

        # 2. Safety Stock: SS = Z * sigma_demand * sqrt(L)
        # Combine demand uncertainty with lead time
        safety_stock = int(math.ceil(z_score * historical_demand_std * math.sqrt(L)))

        # 3. Reorder Point: ROP = Lead_Time_Demand + Safety_Stock
        reorder_point = int(math.ceil(lead_time_demand + safety_stock))

        # 4. Target Operating Inventory Capacity: S_target = LTD + Review_Period_Demand + SS
        review_period_demand = avg_daily_demand * R
        target_inventory = int(math.ceil(lead_time_demand + review_period_demand + safety_stock))

        # 5. Risk Classification
        risk_status, reason = RiskClassifier.classify(
            current_stock=current_stock,
            lead_time_demand=lead_time_demand,
            reorder_point=reorder_point,
            target_inventory=target_inventory,
        )

        # 6. Recommended Reorder Quantity (ROQ)
        # Order up to target inventory if effective inventory (on-hand + on-order) <= ROP
        effective_inventory = current_stock + stock_on_order
        if effective_inventory <= reorder_point:
            raw_order_qty = target_inventory - effective_inventory
            # Apply MOQ and pack size batching
            order_qty = max(min_order_qty, raw_order_qty)
            if pack_size > 1:
                order_qty = int(math.ceil(order_qty / pack_size) * pack_size)
        else:
            order_qty = 0

        # Estimated Days of Supply on Hand
        days_of_supply = round(current_stock / avg_daily_demand, 1) if avg_daily_demand > 0 else 999.0

        return {
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "store_id": store_id,
            "current_stock": current_stock,
            "stock_on_order": stock_on_order,
            "days_of_supply": days_of_supply,
            "avg_daily_forecast_demand": round(avg_daily_demand, 2),
            "lead_time_days": L,
            "service_level": SL,
            "lead_time_demand": round(lead_time_demand, 1),
            "safety_stock": safety_stock,
            "reorder_point": reorder_point,
            "target_inventory": target_inventory,
            "recommended_reorder_qty": order_qty,
            "risk_status": risk_status.value,
            "recommendation_reason": reason,
        }
