"""
Executive Dashboard Analytics Service
====================================
"""

import os
import json
import pandas as pd
from typing import Dict, Any, List
from backend.app.core.config import settings
from backend.app.schemas.schemas import DashboardSummaryResponse
from ml.forecasting.registry import ModelRegistry


class DashboardService:
    """Aggregates executive KPIs, sales trends, category shares, and model metrics."""

    def __init__(self):
        self.registry = ModelRegistry(registry_dir=settings.MODEL_REGISTRY_PATH)

    def get_summary(self) -> DashboardSummaryResponse:
        df = pd.read_csv(settings.DATA_PATH)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Revenue"] = df["Units_Sold"] * df["Price"]

        total_units = int(df["Units_Sold"].sum())
        total_rev = float(df["Revenue"].sum())
        daily_sales = df.groupby("Date")["Units_Sold"].sum()
        avg_daily = float(daily_sales.mean())

        # Category distribution
        cat_df = (
            df.groupby("Category")
            .agg(Units=("Units_Sold", "sum"), Revenue=("Revenue", "sum"))
            .reset_index()
        )
        cat_list = [
            {"category": row["Category"], "units": int(row["Units"]), "revenue": round(float(row["Revenue"]), 2)}
            for _, row in cat_df.iterrows()
        ]

        # Recent 30 days trend
        recent_cutoff = df["Date"].max() - pd.Timedelta(days=30)
        recent_df = df[df["Date"] >= recent_cutoff]
        trend_df = recent_df.groupby("Date")["Units_Sold"].sum().reset_index()
        trend_list = [
            {"date": row["Date"].strftime("%Y-%m-%d"), "units_sold": int(row["Units_Sold"])}
            for _, row in trend_df.iterrows()
        ]

        # Champion Model metadata
        meta = self.registry.load_champion_metadata()
        m_name = meta.get("model_name", "LightGBM")
        m_mae = meta.get("metrics", {}).get("MAE", 5.34)
        m_wape = meta.get("metrics", {}).get("WAPE_pct", 16.09)

        # Inventory risk counts on latest day snapshot
        latest_date = df["Date"].max()
        snapshot = df[df["Date"] == latest_date]
        # Estimate stockout and low stock
        low_stock = int((snapshot["Inventory_Level"] < 150).sum())
        stockout = int((snapshot["Inventory_Level"] < 80).sum())
        overstock = int((snapshot["Inventory_Level"] > 400).sum())
        healthy = len(snapshot) - (low_stock + stockout + overstock)

        return DashboardSummaryResponse(
            total_sales_volume=total_units,
            total_revenue=round(total_rev, 2),
            avg_daily_system_demand=round(avg_daily, 1),
            total_active_products=int(df["Product_ID"].nunique()),
            total_active_stores=int(df["Store_ID"].nunique()),
            low_stock_count=max(0, low_stock),
            stockout_risk_count=max(0, stockout),
            overstock_risk_count=max(0, overstock),
            healthy_count=max(0, healthy),
            champion_model_name=m_name,
            champion_model_mae=m_mae,
            champion_model_wape_pct=m_wape,
            category_distribution=cat_list,
            recent_sales_trend=trend_list,
        )


dashboard_service = DashboardService()
