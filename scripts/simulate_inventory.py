"""
Inventory Optimization & What-If Simulation CLI
===============================================
Generates reorder recommendations across all SKUs and runs a What-If demand shock scenario.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import pandas as pd
from rich.console import Console
from rich.table import Table

from ml.inference.forecaster import MultiHorizonForecaster
from ml.inference.optimizer import InventoryOptimizer
from ml.inference.scenario_simulator import ScenarioSimulator

console = Console()


def run_inventory_optimization():
    console.print("\n[bold cyan]1. Loading Historical Dataset & Champion Model...[/bold cyan]")
    df = pd.read_csv("data/processed/cleaned_sales_data.csv")
    forecaster = MultiHorizonForecaster()
    optimizer = InventoryOptimizer()
    simulator = ScenarioSimulator(forecaster=forecaster, optimizer=optimizer)

    # Get latest active store-product inventory snapshot
    latest_date = df["Date"].max()
    snapshot = df[df["Date"] == latest_date].copy()

    recommendations = []
    console.print(f"\n[bold cyan]2. Generating 14-Day Demand Forecasts & Replenishment Policies ({len(snapshot)} SKUs)...[/bold cyan]")

    for _, row in snapshot.iterrows():
        s_id = row["Store_ID"]
        p_id = row["Product_ID"]
        stock = int(row["Inventory_Level"])
        # SKU demand std
        sku_hist = df[(df["Store_ID"] == s_id) & (df["Product_ID"] == p_id)]
        hist_std = float(sku_hist["Units_Sold"].std()) if len(sku_hist) > 1 else 5.0

        forecast_df = forecaster.forecast(df, store_id=s_id, product_id=p_id, horizon_days=14)
        demands = forecast_df["Predicted_Demand"].tolist()

        opt = optimizer.optimize_sku(
            product_id=p_id,
            product_name=row["Product_Name"],
            category=row["Category"],
            store_id=s_id,
            current_stock=stock,
            forecast_daily_demands=demands,
            historical_demand_std=hist_std,
            lead_time_days=5,
            service_level=0.95,
        )
        recommendations.append(opt)

    # Display Recommendations Table
    rec_table = Table(title="Inventory Position & Reorder Recommendations (14-Day Horizon)", header_style="bold magenta")
    rec_table.add_column("Store", style="cyan")
    rec_table.add_column("Product Name", style="bold")
    rec_table.add_column("Current Stock", justify="right")
    rec_table.add_column("14d Forecast", justify="right")
    rec_table.add_column("Safety Stock", justify="right")
    rec_table.add_column("ROP", justify="right")
    rec_table.add_column("Reorder Qty", justify="right", style="bold green")
    rec_table.add_column("Risk Status", justify="center")

    for r in recommendations[:10]:
        status_style = "green"
        if r["risk_status"] == "STOCKOUT_RISK":
            status_style = "bold red"
        elif r["risk_status"] == "LOW_STOCK":
            status_style = "bold yellow"
        elif r["risk_status"] == "OVERSTOCK_RISK":
            status_style = "bold blue"

        rec_table.add_row(
            r["store_id"],
            r["product_name"][:25],
            f"{r['current_stock']:,}",
            f"{r['avg_daily_forecast_demand'] * 14:.0f}",
            f"{r['safety_stock']}",
            f"{r['reorder_point']}",
            f"{r['recommended_reorder_qty']:,}",
            f"[{status_style}]{r['risk_status']}[/{status_style}]",
        )

    console.print("\n")
    console.print(rec_table)

    # 3. Run What-If Scenario Sandbox
    console.print("\n[bold cyan]3. Running What-If Simulation Sandbox (+25% Demand Spike, 99% Service Level)...[/bold cyan]")
    sim_result = simulator.simulate(
        historical_df=df,
        store_id="STR_01",
        product_id="PRD_01",
        current_stock=120,
        scenario_params={
            "demand_growth_pct": 25.0,
            "service_level": 0.99,
            "lead_time_days": 7,
        },
    )

    comp = sim_result["comparison"]
    sim_table = Table(title=f"What-If Simulation Sandbox: {sim_result['product_name']} (STR_01)", header_style="bold yellow")
    sim_table.add_column("Metric", style="bold")
    sim_table.add_column("Baseline (95% SL)", justify="right")
    sim_table.add_column("Scenario (+25% Demand, 99% SL)", justify="right", style="bold cyan")
    sim_table.add_column("Delta", justify="right", style="bold green")

    sim_table.add_row("14-Day Demand", f"{comp['total_forecast_demand']['baseline']} units", f"{comp['total_forecast_demand']['scenario']} units", f"+{comp['total_forecast_demand']['delta_percentage']}%")
    sim_table.add_row("Safety Stock", f"{comp['safety_stock']['baseline']} units", f"{comp['safety_stock']['scenario']} units", f"+{comp['safety_stock']['delta_units']} units")
    sim_table.add_row("Reorder Point (ROP)", f"{comp['reorder_point']['baseline']} units", f"{comp['reorder_point']['scenario']} units", f"+{comp['reorder_point']['delta_units']} units")
    sim_table.add_row("Recommended Order Qty", f"{comp['recommended_order_qty']['baseline']} units", f"{comp['recommended_order_qty']['scenario']} units", f"+{comp['recommended_order_qty']['delta_units']} units")
    sim_table.add_row("Risk Status", f"{comp['risk_status']['baseline']}", f"{comp['risk_status']['scenario']}", "Risk Transition")

    console.print(sim_table)
    console.print("\n[bold green][OK] Inventory optimization & scenario simulations executed successfully![/bold green]\n")


if __name__ == "__main__":
    run_inventory_optimization()
