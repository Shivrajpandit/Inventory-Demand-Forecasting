"""
Stores & Products Catalog Endpoints
===================================
"""

from typing import List
import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.entities import Product, Store
from backend.app.schemas.schemas import ProductSchema, StoreSchema
from backend.app.core.config import settings

router = APIRouter(tags=["Catalog"])


@router.get("/products", response_model=List[ProductSchema])
def list_products(db: Session = Depends(get_db)):
    # Query DB or fallback to dataset
    products = db.query(Product).all()
    if products:
        return products

    # Read from processed data
    df = pd.read_csv(settings.DATA_PATH)
    meta = df[["Product_ID", "Product_Name", "Category", "Price"]].drop_duplicates(subset=["Product_ID"])
    items = []
    for _, row in meta.iterrows():
        items.append(
            ProductSchema(
                product_id=row["Product_ID"],
                product_name=row["Product_Name"],
                category=row["Category"],
                unit_price=float(row["Price"]),
                unit_cost=round(float(row["Price"]) * 0.55, 2),
                lead_time_days=5,
                min_order_qty=10,
            )
        )
    return items


@router.get("/stores", response_model=List[StoreSchema])
def list_stores(db: Session = Depends(get_db)):
    stores = db.query(Store).all()
    if stores:
        return stores

    df = pd.read_csv(settings.DATA_PATH)
    meta = df[["Store_ID", "Store_Name"]].drop_duplicates(subset=["Store_ID"])
    items = []
    locations = {
        "STR_01": "New York, NY",
        "STR_02": "Austin, TX",
        "STR_03": "Seattle, WA",
    }
    for _, row in meta.iterrows():
        s_id = row["Store_ID"]
        items.append(
            StoreSchema(
                store_id=s_id,
                store_name=row["Store_Name"],
                location=locations.get(s_id, "Retail Center"),
                region="North America",
            )
        )
    return items
