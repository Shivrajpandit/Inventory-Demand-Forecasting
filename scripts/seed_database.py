"""
Database Seeding Script
=======================
Populates database with default user accounts, store and product catalogs,
and inventory levels.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from rich.console import Console
from backend.app.database.session import engine, SessionLocal, Base
from backend.app.models.entities import User, Store, Product, Sale, Inventory
from backend.app.core.security import get_password_hash

console = Console()

STORE_NAMES = {
    "STR_01": "Downtown Metro Mart",
    "STR_02": "Suburban Center",
    "STR_03": "Highland Superstore",
}

STORE_LOCATIONS = {
    "STR_01": "New York, NY",
    "STR_02": "Austin, TX",
    "STR_03": "Seattle, WA",
}


def seed():
    console.print("[bold cyan]1. Initializing Database Schema Tables...[/bold cyan]")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Seed Users
        if not db.query(User).filter(User.email == "demo@inventoryai.com").first():
            console.print("  Creating demo user (demo@inventoryai.com / password123)...")
            demo_user = User(
                email="demo@inventoryai.com",
                hashed_password=get_password_hash("password123"),
                full_name="Demo Inventory Planner",
                role="inventory_planner",
            )
            admin_user = User(
                email="admin@inventoryai.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role="admin",
            )
            db.add_all([demo_user, admin_user])
            db.commit()

        # Seed Stores and Products from dataset
        data_path = "data/processed/cleaned_sales_data.csv"
        if os.path.exists(data_path):
            console.print(f"  Ingesting catalog and sales from {data_path}...")
            df = pd.read_csv(data_path)

            # Stores
            unique_stores = df["Store_ID"].unique()
            for s_id in unique_stores:
                if not db.query(Store).filter(Store.store_id == s_id).first():
                    db.add(Store(
                        store_id=s_id,
                        store_name=STORE_NAMES.get(s_id, f"Store {s_id}"),
                        location=STORE_LOCATIONS.get(s_id, "Retail Location"),
                        region="North America",
                    ))
            db.commit()

            # Products
            prod_meta = df[["Product_ID", "Product_Name", "Category", "Price"]].drop_duplicates(subset=["Product_ID"])
            for _, r in prod_meta.iterrows():
                if not db.query(Product).filter(Product.product_id == r["Product_ID"]).first():
                    price = float(r["Price"])
                    db.add(Product(
                        product_id=r["Product_ID"],
                        product_name=r["Product_Name"],
                        category=r["Category"],
                        unit_price=price,
                        unit_cost=round(price * 0.55, 2),
                        lead_time_days=5,
                        min_order_qty=10,
                    ))
            db.commit()

            # Inventory snapshot
            latest_date = df["Date"].max()
            snap = df[df["Date"] == latest_date]
            for _, r in snap.iterrows():
                existing_inv = db.query(Inventory).filter(
                    Inventory.store_id == r["Store_ID"],
                    Inventory.product_id == r["Product_ID"],
                ).first()
                if not existing_inv:
                    db.add(Inventory(
                        store_id=r["Store_ID"],
                        product_id=r["Product_ID"],
                        current_stock=int(r["Inventory_Level"]),
                        safety_stock=50,
                        reorder_point=150,
                        max_capacity=1000,
                    ))
            db.commit()

        console.print("[bold green][OK] Database seeded successfully![/bold green]")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
