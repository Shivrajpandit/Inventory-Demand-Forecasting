"""
Inventory Stock Risk Classifier
===============================
Classifies SKU stock positions into transparent operational risk tiers:
- 🔴 STOCKOUT_RISK
- 🟠 LOW_STOCK
- 🟢 HEALTHY
- 🔵 OVERSTOCK_RISK
"""

from enum import Enum
from typing import Dict, Any, Tuple


class InventoryRiskStatus(str, Enum):
    STOCKOUT_RISK = "STOCKOUT_RISK"
    LOW_STOCK = "LOW_STOCK"
    HEALTHY = "HEALTHY"
    OVERSTOCK_RISK = "OVERSTOCK_RISK"


class RiskClassifier:
    """Evaluates stock levels against dynamic reorder thresholds and lead time demand."""

    @staticmethod
    def classify(
        current_stock: int,
        lead_time_demand: float,
        reorder_point: int,
        target_inventory: int,
        overstock_threshold_multiplier: float = 1.4,
    ) -> Tuple[InventoryRiskStatus, str]:
        """
        Classifies current stock position and generates actionable justification text.

        Args:
            current_stock: Units currently available on hand.
            lead_time_demand: Expected units consumed during supplier lead time.
            reorder_point: Calculated safety threshold triggering replenishment.
            target_inventory: Maximum target operational inventory capacity.
            overstock_threshold_multiplier: Multiplier above target inventory considered overstock.

        Returns:
            Tuple of (InventoryRiskStatus, reason_string).
        """
        overstock_limit = int(target_inventory * overstock_threshold_multiplier)

        # 1. Critical Stockout Risk
        if current_stock < lead_time_demand:
            reason = (
                f"CRITICAL: Current stock ({current_stock:,} units) is below projected lead-time demand "
                f"({lead_time_demand:.1f} units). Imminent stockout before supplier replenishment arrives."
            )
            return InventoryRiskStatus.STOCKOUT_RISK, reason

        # 2. Low Stock (Below or at Reorder Point)
        elif current_stock <= reorder_point:
            reason = (
                f"REORDER RECOMMENDED: Current stock ({current_stock:,} units) is at or below Reorder Point "
                f"({reorder_point:,} units). Standard replenishment purchase order should be placed."
            )
            return InventoryRiskStatus.LOW_STOCK, reason

        # 3. Overstock Risk
        elif current_stock > overstock_limit:
            reason = (
                f"OVERSTOCK ALERT: Current stock ({current_stock:,} units) exceeds target operating capacity "
                f"({target_inventory:,} units) by {round(((current_stock - target_inventory) / target_inventory) * 100)}%. "
                f"Risk of tied-up capital and holding cost."
            )
            return InventoryRiskStatus.OVERSTOCK_RISK, reason

        # 4. Healthy
        else:
            reason = (
                f"HEALTHY: Current stock ({current_stock:,} units) is within optimal operating range "
                f"(Reorder Point: {reorder_point:,} | Target: {target_inventory:,}). No action required."
            )
            return InventoryRiskStatus.HEALTHY, reason
