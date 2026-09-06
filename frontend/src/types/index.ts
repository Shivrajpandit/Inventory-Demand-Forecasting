export interface Product {
  product_id: string;
  product_name: string;
  category: string;
  unit_price: number;
  unit_cost: number;
  lead_time_days: number;
  min_order_qty: number;
}

export interface Store {
  store_id: string;
  store_name: string;
  location: string;
  region: string;
}

export interface DailyForecastItem {
  date: string;
  day_of_week: string;
  predicted_demand: number;
  lower_bound: number;
  upper_bound: number;
  promotion: number;
  price: number;
}

export interface ForecastResponse {
  store_id: string;
  product_id: string;
  product_name: string;
  category: string;
  horizon_days: number;
  model_used: string;
  total_forecast_demand: number;
  avg_daily_demand: number;
  daily_forecasts: DailyForecastItem[];
}

export interface InventoryStatusItem {
  product_id: string;
  product_name: string;
  category: string;
  store_id: string;
  current_stock: number;
  stock_on_order: number;
  days_of_supply: number;
  avg_daily_forecast_demand: number;
  lead_time_days: number;
  service_level: number;
  lead_time_demand: number;
  safety_stock: number;
  reorder_point: number;
  target_inventory: number;
  recommended_reorder_qty: number;
  risk_status: 'HEALTHY' | 'LOW_STOCK' | 'STOCKOUT_RISK' | 'OVERSTOCK_RISK';
  recommendation_reason: string;
}

export interface InventorySummaryResponse {
  total_products_tracked: number;
  total_inventory_units: number;
  stockout_risk_count: number;
  low_stock_count: number;
  healthy_count: number;
  overstock_risk_count: number;
  total_recommended_reorder_units: number;
  items: InventoryStatusItem[];
}

export interface DashboardSummaryResponse {
  total_sales_volume: number;
  total_revenue: number;
  avg_daily_system_demand: number;
  total_active_products: number;
  total_active_stores: number;
  low_stock_count: number;
  stockout_risk_count: number;
  overstock_risk_count: number;
  healthy_count: number;
  champion_model_name: string;
  champion_model_mae: number;
  champion_model_wape_pct: number;
  category_distribution: Array<{ category: string; units: number; revenue: number }>;
  recent_sales_trend: Array<{ date: string; units_sold: number }>;
}

export interface ScenarioSimulationResult {
  store_id: string;
  product_id: string;
  product_name: string;
  scenario_parameters: Record<string, any>;
  comparison: {
    total_forecast_demand: { baseline: number; scenario: number; delta_percentage: number };
    safety_stock: { baseline: number; scenario: number; delta_units: number };
    reorder_point: { baseline: number; scenario: number; delta_units: number };
    recommended_order_qty: { baseline: number; scenario: number; delta_units: number };
    risk_status: { baseline: string; scenario: string };
  };
  daily_forecast_curves: {
    dates: string[];
    baseline_demand: number[];
    scenario_demand: number[];
  };
}
