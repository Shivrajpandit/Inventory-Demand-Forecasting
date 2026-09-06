"""
Synthetic Retail Sales Data Generator
====================================
Generates realistic, physically-grounded multi-store retail sales datasets
incorporating calendar seasonality, holiday surges, promotional elasticity,
and inventory stockout dynamics for testing and development.
"""

import os
import argparse
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


# Store Profiles
STORES = [
    {"Store_ID": "STR_01", "Store_Name": "Downtown Metro Mart", "Location": "New York, NY", "Base_Multiplier": 1.25},
    {"Store_ID": "STR_02", "Store_Name": "Suburban Center", "Location": "Austin, TX", "Base_Multiplier": 1.00},
    {"Store_ID": "STR_03", "Store_Name": "Highland Superstore", "Location": "Seattle, WA", "Base_Multiplier": 0.85},
]

# Product Catalog
PRODUCTS = [
    {"Product_ID": "PRD_01", "Product_Name": "Organic Whole Milk 1 Gal", "Category": "Dairy", "Base_Price": 4.99, "Cost": 2.80, "Base_Daily_Demand": 45, "Volatility": 0.15, "Lead_Time": 3},
    {"Product_ID": "PRD_02", "Product_Name": "Artisan Sourdough Bread", "Category": "Bakery", "Base_Price": 3.49, "Cost": 1.50, "Base_Daily_Demand": 30, "Volatility": 0.20, "Lead_Time": 2},
    {"Product_ID": "PRD_03", "Product_Name": "Cold Brew Coffee 32oz", "Category": "Beverages", "Base_Price": 5.99, "Cost": 3.10, "Base_Daily_Demand": 25, "Volatility": 0.25, "Lead_Time": 5},
    {"Product_ID": "PRD_04", "Product_Name": "Greek Yogurt Vanilla 32oz", "Category": "Dairy", "Base_Price": 4.49, "Cost": 2.20, "Base_Daily_Demand": 28, "Volatility": 0.18, "Lead_Time": 4},
    {"Product_ID": "PRD_05", "Product_Name": "Organic Free-Range Eggs 12ct", "Category": "Dairy", "Base_Price": 4.29, "Cost": 2.40, "Base_Daily_Demand": 50, "Volatility": 0.12, "Lead_Time": 3},
    {"Product_ID": "PRD_06", "Product_Name": "Sparkling Mineral Water 12pk", "Category": "Beverages", "Base_Price": 6.99, "Cost": 3.80, "Base_Daily_Demand": 35, "Volatility": 0.22, "Lead_Time": 7},
    {"Product_ID": "PRD_07", "Product_Name": "Gourmet Dark Chocolate 85%", "Category": "Snacks", "Base_Price": 3.99, "Cost": 1.90, "Base_Daily_Demand": 20, "Volatility": 0.30, "Lead_Time": 7},
    {"Product_ID": "PRD_08", "Product_Name": "Organic Quinoa 2lb", "Category": "Pantry", "Base_Price": 7.49, "Cost": 4.00, "Base_Daily_Demand": 15, "Volatility": 0.15, "Lead_Time": 10},
    {"Product_ID": "PRD_09", "Product_Name": "Extra Virgin Olive Oil 500ml", "Category": "Pantry", "Base_Price": 12.99, "Cost": 7.50, "Base_Daily_Demand": 12, "Volatility": 0.15, "Lead_Time": 14},
    {"Product_ID": "PRD_10", "Product_Name": "Roasted Almonds Salted 16oz", "Category": "Snacks", "Base_Price": 8.99, "Cost": 4.80, "Base_Daily_Demand": 22, "Volatility": 0.20, "Lead_Time": 7},
]

# Major Holiday Offsets (Month, Day, Demand Boost Factor)
HOLIDAYS = [
    (1, 1, 1.35),   # New Year's Day
    (2, 14, 1.25),  # Valentine's Day
    (5, 27, 1.40),  # Memorial Day
    (7, 4, 1.50),   # Independence Day
    (9, 2, 1.35),   # Labor Day
    (11, 24, 1.70), # Thanksgiving season
    (12, 24, 1.85), # Christmas Eve
    (12, 25, 0.40), # Christmas Day (Stores partially closed)
    (12, 31, 1.65), # New Year's Eve
]


def generate_retail_dataset(
    start_date: str = "2024-01-01",
    days: int = 730,
    seed: int = 42,
) -> pd.DataFrame:
    """Generates synthetic multi-SKU retail sales with authentic time-series patterns."""
    np.random.seed(seed)
    start = datetime.strptime(start_date, "%Y-%m-%d")
    date_range = [start + timedelta(days=i) for i in range(days)]

    records = []

    for store in STORES:
        for product in PRODUCTS:
            # Persistent inventory tracker for simulation
            current_inventory = product["Base_Daily_Demand"] * 10

            for d in date_range:
                # 1. Base demand with store sizing
                base_demand = product["Base_Daily_Demand"] * store["Base_Multiplier"]

                # 2. Weekly Seasonality: Friday/Saturday/Sunday peak
                dow = d.weekday()  # 0=Monday, 6=Sunday
                dow_factors = [0.85, 0.90, 0.95, 1.05, 1.30, 1.45, 1.20]
                dow_multiplier = dow_factors[dow]

                # 3. Monthly/Seasonal variation (sinusoidal)
                month = d.month
                # Summer peaks for Beverages (month 6-8), Winter peaks for Bakery/Pantry
                if product["Category"] == "Beverages":
                    month_multiplier = 1.0 + 0.25 * np.sin((month - 3) * np.pi / 6)
                elif product["Category"] in ["Bakery", "Pantry"]:
                    month_multiplier = 1.0 + 0.15 * np.cos((month - 1) * np.pi / 6)
                else:
                    month_multiplier = 1.0 + 0.08 * np.sin((month - 1) * np.pi / 6)

                # 4. Holiday effect
                is_holiday = 0
                holiday_multiplier = 1.0
                for h_m, h_d, h_boost in HOLIDAYS:
                    if d.month == h_m and abs(d.day - h_d) <= 1:
                        is_holiday = 1
                        holiday_multiplier = h_boost
                        break

                # 5. Promotions & Discounts (Occurs periodically every ~3-4 weeks)
                promo_cycle = (d.timetuple().tm_yday + int(product["Product_ID"][-2:])) % 25
                is_promo = 1 if promo_cycle < 4 else 0
                discount = 0.15 if is_promo else 0.0
                promo_multiplier = 1.45 if is_promo else 1.0

                # 6. Price adjustment
                unit_price = round(product["Base_Price"] * (1.0 - discount), 2)

                # 7. Final Expected Demand with stochastic noise
                expected_demand = base_demand * dow_multiplier * month_multiplier * holiday_multiplier * promo_multiplier
                noise = np.random.normal(1.0, product["Volatility"])
                actual_demand = max(0, int(round(expected_demand * noise)))

                # 8. Inventory & Stockout Dynamics
                # Replenish if inventory gets low
                if current_inventory <= product["Base_Daily_Demand"] * 3:
                    # Reorder arrives
                    current_inventory += int(product["Base_Daily_Demand"] * 8)

                # Sold units cannot exceed stock on hand
                units_sold = min(actual_demand, current_inventory)
                current_inventory -= units_sold

                # Season label
                if month in [12, 1, 2]:
                    season = "Winter"
                elif month in [3, 4, 5]:
                    season = "Spring"
                elif month in [6, 7, 8]:
                    season = "Summer"
                else:
                    season = "Autumn"

                records.append({
                    "Date": d.strftime("%Y-%m-%d"),
                    "Store_ID": store["Store_ID"],
                    "Store_Name": store["Store_Name"],
                    "Product_ID": product["Product_ID"],
                    "Product_Name": product["Product_Name"],
                    "Category": product["Category"],
                    "Units_Sold": units_sold,
                    "Price": unit_price,
                    "Discount": discount,
                    "Promotion": is_promo,
                    "Holiday": is_holiday,
                    "Day_of_Week": dow,
                    "Month": month,
                    "Season": season,
                    "Inventory_Level": current_inventory,
                })

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic retail sales dataset.")
    parser.add_argument("--days", type=int, default=730, help="Number of historical days to generate.")
    parser.add_argument("--output", type=str, default="data/raw/sales_data.csv", help="Output CSV path.")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df = generate_retail_dataset(days=args.days)
    df.to_csv(args.output, index=False)

    # Also save a sample slice for testing
    sample_path = "data/sample/sample_sales.csv"
    os.makedirs(os.path.dirname(sample_path), exist_ok=True)
    df.head(500).to_csv(sample_path, index=False)

    print(f"Generated {len(df):,} retail sales records spanning {args.days} days.")
    print(f"Saved to: {args.output}")
    print(f"Sample saved to: {sample_path}")
