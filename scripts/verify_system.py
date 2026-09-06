"""
Master System Diagnostic & Verification Suite
=============================================
Runs sanity checks across data pipelines, model registry, database records,
and REST API endpoints, outputting an executive verification report.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import pandas as pd
from rich.console import Console
from rich.table import Table
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.session import SessionLocal
from backend.app.models.entities import User, Store, Product, Inventory
from ml.forecasting.registry import ModelRegistry

console = Console()


def run_system_verification():
    console.print("\n[bold blue]================================================================[/bold blue]")
    console.print("[bold cyan]  AI Inventory Demand Forecasting - Full System Verification Suite [/bold cyan]")
    console.print("[bold blue]================================================================[/bold blue]\n")

    table = Table(title="System Component Health & Verification Checks", header_style="bold magenta")
    table.add_column("Component", style="bold")
    table.add_column("Details", style="cyan")
    table.add_column("Status", justify="center")

    all_passed = True

    # 1. Dataset Check
    raw_path = "data/raw/sales_data.csv"
    proc_path = "data/processed/cleaned_sales_data.csv"
    if os.path.exists(raw_path) and os.path.exists(proc_path):
        raw_df = pd.read_csv(raw_path)
        proc_df = pd.read_csv(proc_path)
        table.add_row(
            "Retail Datasets",
            f"Raw: {len(raw_df):,} rows | Processed: {len(proc_df):,} rows ({proc_df['Store_ID'].nunique()} stores, {proc_df['Product_ID'].nunique()} SKUs)",
            "[bold green][PASS][/bold green]",
        )
    else:
        table.add_row("Retail Datasets", "Dataset files missing in data/", "[bold red][FAIL][/bold red]")
        all_passed = False

    # 2. Model Registry Check
    registry = ModelRegistry(registry_dir="models")
    champ_path = "models/champion_model.joblib"
    if os.path.exists(champ_path):
        meta = registry.load_champion_metadata()
        m_name = meta.get("model_name", "Unknown")
        m_mae = meta.get("metrics", {}).get("MAE", "N/A")
        table.add_row(
            "Model Registry",
            f"Champion: {m_name} (Test MAE: {m_mae}, WAPE: {meta.get('metrics', {}).get('WAPE_pct')}%)",
            "[bold green][PASS][/bold green]",
        )
    else:
        table.add_row("Model Registry", "Champion model artifact missing in models/", "[bold red][FAIL][/bold red]")
        all_passed = False

    # 3. Database Check
    db = SessionLocal()
    try:
        user_cnt = db.query(User).count()
        prod_cnt = db.query(Product).count()
        store_cnt = db.query(Store).count()
        inv_cnt = db.query(Inventory).count()
        table.add_row(
            "Relational Database",
            f"Users: {user_cnt} | Stores: {store_cnt} | Products: {prod_cnt} | Inventory Items: {inv_cnt}",
            "[bold green][PASS][/bold green]",
        )
    except Exception as e:
        table.add_row("Relational Database", f"DB Error: {str(e)}", "[bold red][FAIL][/bold red]")
        all_passed = False
    finally:
        db.close()

    # 4. REST API Endpoint Checks
    client = TestClient(app)

    # Health
    h_res = client.get("/health")
    if h_res.status_code == 200:
        table.add_row("REST API: /health", "Status: 200 OK (HEALTHY)", "[bold green][PASS][/bold green]")
    else:
        table.add_row("REST API: /health", f"Status: {h_res.status_code}", "[bold red][FAIL][/bold red]")
        all_passed = False

    # Dashboard Summary
    d_res = client.get("/api/dashboard/summary")
    if d_res.status_code == 200:
        d_data = d_res.json()
        table.add_row(
            "REST API: /api/dashboard/summary",
            f"Volume: {d_data['total_sales_volume']:,} units | Rev: ${d_data['total_revenue']:,.2f}",
            "[bold green][PASS][/bold green]",
        )
    else:
        table.add_row("REST API: /api/dashboard/summary", f"Status: {d_res.status_code}", "[bold red][FAIL][/bold red]")
        all_passed = False

    # Forecast API
    f_res = client.post("/api/forecast", json={"store_id": "STR_01", "product_id": "PRD_01", "horizon_days": 14})
    if f_res.status_code == 200:
        f_data = f_res.json()
        table.add_row(
            "REST API: /api/forecast",
            f"14-Day Demand for {f_data['product_name']}: {f_data['total_forecast_demand']} units",
            "[bold green][PASS][/bold green]",
        )
    else:
        table.add_row("REST API: /api/forecast", f"Status: {f_res.status_code}", "[bold red][FAIL][/bold red]")
        all_passed = False

    # Inventory API
    i_res = client.get("/api/inventory/status?store_id=STR_01")
    if i_res.status_code == 200:
        i_data = i_res.json()
        table.add_row(
            "REST API: /api/inventory/status",
            f"Tracked SKUs: {i_data['total_products_tracked']} | Reorder Qty: {i_data['total_recommended_reorder_units']:,} units",
            "[bold green][PASS][/bold green]",
        )
    else:
        table.add_row("REST API: /api/inventory/status", f"Status: {i_res.status_code}", "[bold red][FAIL][/bold red]")
        all_passed = False

    # Scenario Simulation API
    s_res = client.post("/api/scenario/simulate", json={
        "store_id": "STR_01",
        "product_id": "PRD_01",
        "demand_growth_pct": 20.0,
        "service_level": 0.99,
        "lead_time_days": 7,
        "horizon_days": 14,
    })
    if s_res.status_code == 200:
        s_data = s_res.json()
        table.add_row(
            "REST API: /api/scenario/simulate",
            f"Base: {s_data['comparison']['total_forecast_demand']['baseline']}u -> Scenario: {s_data['comparison']['total_forecast_demand']['scenario']}u",
            "[bold green][PASS][/bold green]",
        )
    else:
        table.add_row("REST API: /api/scenario/simulate", f"Status: {s_res.status_code}", "[bold red][FAIL][/bold red]")
        all_passed = False

    console.print(table)

    if all_passed:
        console.print("\n[bold green][OK] ALL SYSTEM COMPONENTS FULLY VERIFIED & HEALTHY![/bold green]\n")
    else:
        console.print("\n[bold red][FAIL] SOME SYSTEM CHECKS FAILED. PLEASE REVIEW LOGS.[/bold red]\n")


if __name__ == "__main__":
    run_system_verification()
