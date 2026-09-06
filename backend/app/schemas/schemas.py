"""
Pydantic v2 Data Schemas for REST API
=====================================
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ------------------------------------------------------------------------------
# Auth Schemas
# ------------------------------------------------------------------------------
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    role: Optional[str] = "inventory_planner"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


# ------------------------------------------------------------------------------
# Store & Product Schemas
# ------------------------------------------------------------------------------
class StoreSchema(BaseModel):
    store_id: str
    store_name: str
    location: str
    region: str

    model_config = ConfigDict(from_attributes=True)


class ProductSchema(BaseModel):
    product_id: str
    product_name: str
    category: str
    unit_price: float
    unit_cost: float
    lead_time_days: int
    min_order_qty: int

    model_config = ConfigDict(from_attributes=True)


# ------------------------------------------------------------------------------
# Forecast Schemas
# ------------------------------------------------------------------------------
class ForecastRequest(BaseModel):
    store_id: str
    product_id: str
    horizon_days: int = Field(default=14, ge=1, le=90)
    demand_growth_pct: Optional[float] = 0.0
    price_change_pct: Optional[float] = 0.0
    is_promotion: Optional[bool] = None


class DailyForecastItem(BaseModel):
    date: str
    day_of_week: str
    predicted_demand: float
    lower_bound: float
    upper_bound: float
    promotion: int
    price: float


class ForecastResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    store_id: str
    product_id: str
    product_name: str
    category: str
    horizon_days: int
    model_used: str
    total_forecast_demand: float
    avg_daily_demand: float
    daily_forecasts: List[DailyForecastItem]


# ------------------------------------------------------------------------------
# Inventory & Recommendation Schemas
# ------------------------------------------------------------------------------
class InventoryStatusItem(BaseModel):
    product_id: str
    product_name: str
    category: str
    store_id: str
    current_stock: int
    stock_on_order: int
    days_of_supply: float
    avg_daily_forecast_demand: float
    lead_time_days: int
    service_level: float
    lead_time_demand: float
    safety_stock: int
    reorder_point: int
    target_inventory: int
    recommended_reorder_qty: int
    risk_status: str
    recommendation_reason: str


class InventorySummaryResponse(BaseModel):
    total_products_tracked: int
    total_inventory_units: int
    stockout_risk_count: int
    low_stock_count: int
    healthy_count: int
    overstock_risk_count: int
    total_recommended_reorder_units: int
    items: List[InventoryStatusItem]


# ------------------------------------------------------------------------------
# What-If Scenario Schemas
# ------------------------------------------------------------------------------
class ScenarioSimulationRequest(BaseModel):
    store_id: str
    product_id: str
    current_stock: Optional[int] = None
    demand_growth_pct: float = 0.0
    price_change_pct: float = 0.0
    lead_time_days: Optional[int] = None
    service_level: Optional[float] = 0.95
    is_promotion: Optional[bool] = None
    horizon_days: int = 14


class ScenarioSaveRequest(BaseModel):
    name: str
    store_id: str
    product_id: str
    input_parameters: Dict[str, Any]
    simulation_results: Dict[str, Any]


# ------------------------------------------------------------------------------
# Dashboard KPI Summary
# ------------------------------------------------------------------------------
class DashboardSummaryResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    total_sales_volume: int
    total_revenue: float
    avg_daily_system_demand: float
    total_active_products: int
    total_active_stores: int
    low_stock_count: int
    stockout_risk_count: int
    overstock_risk_count: int
    healthy_count: int
    champion_model_name: str
    champion_model_mae: float
    champion_model_wape_pct: float
    category_distribution: List[Dict[str, Any]]
    recent_sales_trend: List[Dict[str, Any]]
