"""
Data Cleaning & Preprocessing Module
====================================
Transforms raw sales records into a clean, complete, and reproducible
daily time-series grid per Store and SKU.
"""

from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np


class DataCleaner:
    """Handles data cleansing, imputation, outlier mitigation, and time grid completion."""

    def __init__(
        self,
        clip_negative_sales: bool = True,
        impute_missing_categories: bool = True,
        remove_duplicates: bool = True,
        complete_date_grid: bool = True,
    ):
        self.clip_negative_sales = clip_negative_sales
        self.impute_missing_categories = impute_missing_categories
        self.remove_duplicates = remove_duplicates
        self.complete_date_grid = complete_date_grid

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Executes full cleaning pipeline on input DataFrame."""
        cleaned_df = df.copy()

        # 1. Standardize column names (strip whitespace)
        cleaned_df.columns = [c.strip() for c in cleaned_df.columns]

        # 2. Date parsing and sorting
        cleaned_df["Date"] = pd.to_datetime(cleaned_df["Date"])
        cleaned_df = cleaned_df.dropna(subset=["Date", "Store_ID", "Product_ID"])

        # 3. Handle Duplicates
        if self.remove_duplicates:
            # Group by Store_ID, Product_ID, Date and sum Units_Sold if multiple transactions per day
            agg_rules = {
                "Units_Sold": "sum",
                "Price": "mean",
            }
            # Add other columns to aggregation if present
            for col in ["Product_Name", "Category", "Season"]:
                if col in cleaned_df.columns:
                    agg_rules[col] = "first"
            for col in ["Discount", "Promotion", "Holiday", "Inventory_Level"]:
                if col in cleaned_df.columns:
                    agg_rules[col] = "max"

            cleaned_df = (
                cleaned_df.groupby(["Store_ID", "Product_ID", "Date"], as_index=False)
                .agg(agg_rules)
            )

        # 4. Handle Numeric Types and Invalid/Negative Sales
        cleaned_df["Units_Sold"] = pd.to_numeric(cleaned_df["Units_Sold"], errors="coerce").fillna(0)
        if self.clip_negative_sales:
            # Returns or errors clipped to 0 for demand modeling
            cleaned_df["Units_Sold"] = cleaned_df["Units_Sold"].clip(lower=0)

        if "Price" in cleaned_df.columns:
            cleaned_df["Price"] = pd.to_numeric(cleaned_df["Price"], errors="coerce")
            # Impute missing price with product median price
            product_prices = cleaned_df.groupby("Product_ID")["Price"].transform("median")
            cleaned_df["Price"] = cleaned_df["Price"].fillna(product_prices).fillna(10.0)

        if "Discount" in cleaned_df.columns:
            cleaned_df["Discount"] = pd.to_numeric(cleaned_df["Discount"], errors="coerce").fillna(0.0).clip(0.0, 1.0)
        else:
            cleaned_df["Discount"] = 0.0

        if "Promotion" in cleaned_df.columns:
            cleaned_df["Promotion"] = cleaned_df["Promotion"].astype(int)
        else:
            cleaned_df["Promotion"] = (cleaned_df["Discount"] > 0.05).astype(int)

        if "Holiday" in cleaned_df.columns:
            cleaned_df["Holiday"] = cleaned_df["Holiday"].astype(int)
        else:
            cleaned_df["Holiday"] = 0

        # 5. Impute Missing Metadata (Product Name, Category)
        if self.impute_missing_categories:
            if "Product_Name" in cleaned_df.columns:
                product_names = cleaned_df.groupby("Product_ID")["Product_Name"].transform("first")
                cleaned_df["Product_Name"] = cleaned_df["Product_Name"].fillna(product_names).fillna(cleaned_df["Product_ID"])
            else:
                cleaned_df["Product_Name"] = cleaned_df["Product_ID"]

            if "Category" in cleaned_df.columns:
                product_cats = cleaned_df.groupby("Product_ID")["Category"].transform("first")
                cleaned_df["Category"] = cleaned_df["Category"].fillna(product_cats).fillna("General")
            else:
                cleaned_df["Category"] = "General"

        # 6. Complete Time-Series Date Grid (Crucial for Time-Series Modeling)
        if self.complete_date_grid:
            cleaned_df = self._complete_grid(cleaned_df)

        # 7. Add Standard Calendar Attributes
        cleaned_df["Day_of_Week"] = cleaned_df["Date"].dt.dayofweek
        cleaned_df["Month"] = cleaned_df["Date"].dt.month
        cleaned_df["Is_Weekend"] = (cleaned_df["Day_of_Week"] >= 5).astype(int)
        cleaned_df["Season"] = cleaned_df["Month"].map(self._month_to_season)

        # Sort chronologically
        cleaned_df = cleaned_df.sort_values(["Store_ID", "Product_ID", "Date"]).reset_index(drop=True)
        return cleaned_df

    def _complete_grid(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fills missing daily timestamps for each (Store_ID, Product_ID) pair with 0 demand."""
        min_date = df["Date"].min()
        max_date = df["Date"].max()
        all_dates = pd.date_range(min_date, max_date, freq="D", name="Date")

        # Get unique store-product pairs with static metadata
        meta_cols = ["Store_ID", "Product_ID", "Product_Name", "Category"]
        meta_df = df[meta_cols].drop_duplicates()

        # Cartesian product of metadata and dates
        grid_rows = []
        for _, row in meta_df.iterrows():
            sub = pd.DataFrame({"Date": all_dates})
            for col in meta_cols:
                sub[col] = row[col]
            grid_rows.append(sub)

        full_grid = pd.concat(grid_rows, ignore_index=True)

        # Merge with actual sales data
        merged = pd.merge(
            full_grid,
            df,
            on=["Store_ID", "Product_ID", "Product_Name", "Category", "Date"],
            how="left",
        )

        # Zero-fill missing daily unit sales
        merged["Units_Sold"] = merged["Units_Sold"].fillna(0.0)
        merged["Discount"] = merged["Discount"].fillna(0.0)
        merged["Promotion"] = merged["Promotion"].fillna(0).astype(int)
        merged["Holiday"] = merged["Holiday"].fillna(0).astype(int)

        # Forward/Backward fill prices per product
        merged["Price"] = merged.groupby("Product_ID")["Price"].transform(lambda s: s.ffill().bfill()).fillna(10.0)

        # Inventory Level estimation if present
        if "Inventory_Level" in merged.columns:
            merged["Inventory_Level"] = merged.groupby(["Store_ID", "Product_ID"])["Inventory_Level"].transform(
                lambda s: s.ffill().bfill()
            ).fillna(100.0)
        else:
            merged["Inventory_Level"] = 100.0

        return merged

    @staticmethod
    def _month_to_season(month: int) -> str:
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Autumn"
