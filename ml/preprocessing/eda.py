"""
Exploratory Data Analysis (EDA) Module
======================================
Performs comprehensive statistical, temporal, product, category, and inventory
analysis on cleaned retail time-series records and exports charts & metrics.
"""

import os
import json
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import seaborn as sns


class RetailEDA:
    """Performs full exploratory data analysis and generates summary metrics & figures."""

    def __init__(self, output_dir: str = "docs/eda_reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Setup visual theme
        sns.set_theme(style="whitegrid", palette="deep")
        plt.rcParams["figure.figsize"] = (10, 6)
        plt.rcParams["font.size"] = 10

    def run_full_eda(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Executes end-to-end EDA analysis, writes figures, and returns summary dictionary."""
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        df["Revenue"] = df["Units_Sold"] * df["Price"]

        metrics = {
            "overall": self._analyze_overall(df),
            "products": self._analyze_products(df),
            "categories": self._analyze_categories(df),
            "temporal": self._analyze_temporal(df),
            "business_factors": self._analyze_business_factors(df),
            "inventory": self._analyze_inventory(df),
        }

        # Save metrics summary as JSON
        summary_path = os.path.join(self.output_dir, "eda_summary.json")
        with open(summary_path, "w") as f:
            json.dump(metrics, f, indent=2, default=str)

        print(f"EDA Analysis complete. Figures & summary saved to '{self.output_dir}/'")
        return metrics

    def _analyze_overall(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyzes aggregate revenue, sales volume, and overall trends."""
        total_units = int(df["Units_Sold"].sum())
        total_revenue = float(df["Revenue"].sum())
        daily_sales = df.groupby("Date")["Units_Sold"].sum()
        avg_daily_units = float(daily_sales.mean())
        std_daily_units = float(daily_sales.std())

        # Plot Overall Sales Trend
        plt.figure(figsize=(12, 5))
        daily_sales.plot(color="#2563eb", linewidth=1.5)
        daily_sales.rolling(window=14).mean().plot(color="#dc2626", linewidth=2.0, label="14-Day Moving Avg")
        plt.title("Total Daily Retail Unit Sales Trend", fontsize=14, fontweight="bold", pad=12)
        plt.xlabel("Date", fontsize=11)
        plt.ylabel("Total Units Sold", fontsize=11)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "01_overall_sales_trend.png"), dpi=150)
        plt.close()

        # Plot Sales Distribution
        plt.figure(figsize=(10, 5))
        sns.histplot(df["Units_Sold"], bins=40, kde=True, color="#0284c7")
        plt.title("Distribution of Daily Store-SKU Units Sold", fontsize=14, fontweight="bold", pad=12)
        plt.xlabel("Units Sold", fontsize=11)
        plt.ylabel("Frequency", fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "02_sales_distribution.png"), dpi=150)
        plt.close()

        return {
            "total_units_sold": total_units,
            "total_revenue": round(total_revenue, 2),
            "avg_daily_units": round(avg_daily_units, 2),
            "std_daily_units": round(std_daily_units, 2),
            "total_records": len(df),
            "date_start": df["Date"].min().strftime("%Y-%m-%d"),
            "date_end": df["Date"].max().strftime("%Y-%m-%d"),
        }

    def _analyze_products(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyzes top and low selling products and demand velocity."""
        product_summary = (
            df.groupby(["Product_ID", "Product_Name", "Category"])
            .agg(
                Total_Units=("Units_Sold", "sum"),
                Avg_Daily_Units=("Units_Sold", "mean"),
                Std_Daily_Units=("Units_Sold", "std"),
                Total_Revenue=("Revenue", "sum"),
            )
            .reset_index()
            .sort_values(by="Total_Units", ascending=False)
        )

        top_5 = product_summary.head(5).to_dict(orient="records")
        bottom_5 = product_summary.tail(5).to_dict(orient="records")

        # Plot Product Sales Volume
        plt.figure(figsize=(12, 6))
        sns.barplot(data=product_summary, x="Total_Units", y="Product_Name", hue="Product_Name", palette="viridis", legend=False)
        plt.title("Total Sales Volume by SKU (All Stores)", fontsize=14, fontweight="bold", pad=12)
        plt.xlabel("Cumulative Units Sold", fontsize=11)
        plt.ylabel("Product Name", fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "03_product_demand_ranking.png"), dpi=150)
        plt.close()

        return {
            "top_selling_products": top_5,
            "lowest_selling_products": bottom_5,
        }

    def _analyze_categories(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyzes category breakdown and contribution."""
        category_summary = (
            df.groupby("Category")
            .agg(
                Total_Units=("Units_Sold", "sum"),
                Total_Revenue=("Revenue", "sum"),
                Avg_Daily_Units=("Units_Sold", "mean"),
            )
            .reset_index()
            .sort_values(by="Total_Revenue", ascending=False)
        )

        # Plot Category Contribution Pie / Bar
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        axes[0].pie(
            category_summary["Total_Revenue"],
            labels=category_summary["Category"],
            autopct="%1.1f%%",
            colors=sns.color_palette("Set2"),
            startangle=140,
        )
        axes[0].set_title("Revenue Share by Product Category", fontsize=13, fontweight="bold")

        sns.barplot(
            data=category_summary,
            x="Category",
            y="Total_Units",
            hue="Category",
            ax=axes[1],
            palette="Set2",
            legend=False,
        )
        axes[1].set_title("Total Units Sold by Category", fontsize=13, fontweight="bold")
        axes[1].set_ylabel("Units Sold")

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "04_category_breakdown.png"), dpi=150)
        plt.close()

        return {"categories": category_summary.to_dict(orient="records")}

    def _analyze_temporal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyzes day-of-week, monthly, and seasonal demand variations."""
        dow_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        df["DOW_Name"] = df["Day_of_Week"].map(lambda x: dow_names[int(x)])

        dow_summary = (
            df.groupby("DOW_Name", as_index=False)["Units_Sold"]
            .mean()
            .sort_values(by="Units_Sold", ascending=False)
        )

        seasonal_summary = df.groupby("Season", as_index=False)["Units_Sold"].mean()

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        sns.barplot(
            data=df,
            x="Day_of_Week",
            y="Units_Sold",
            hue="Day_of_Week",
            ax=axes[0],
            palette="Blues_d",
            errorbar=None,
            legend=False,
        )
        axes[0].set_xticks(range(7))
        axes[0].set_xticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        axes[0].set_title("Average Daily Demand by Day of Week", fontsize=13, fontweight="bold")
        axes[0].set_ylabel("Average Units Sold")

        sns.lineplot(
            data=df,
            x="Month",
            y="Units_Sold",
            hue="Category",
            ax=axes[1],
            marker="o",
            errorbar=None,
        )
        axes[1].set_title("Monthly Seasonality by Category", fontsize=13, fontweight="bold")
        axes[1].set_xticks(range(1, 13))
        axes[1].set_ylabel("Average Units Sold")

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "05_temporal_seasonality.png"), dpi=150)
        plt.close()

        return {
            "dow_ranking": dow_summary.to_dict(orient="records"),
            "seasonal_summary": seasonal_summary.to_dict(orient="records"),
        }

    def _analyze_business_factors(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyzes impact of promotions, discounts, and holidays on sales."""
        promo_impact = df.groupby("Promotion")["Units_Sold"].mean().to_dict()
        holiday_impact = df.groupby("Holiday")["Units_Sold"].mean().to_dict()

        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        sns.boxplot(
            data=df,
            x="Promotion",
            y="Units_Sold",
            hue="Promotion",
            ax=axes[0],
            palette=["#94a3b8", "#10b981"],
            showfliers=False,
            legend=False,
        )
        axes[0].set_xticks([0, 1])
        axes[0].set_xticklabels(["Standard (No Promo)", "Active Promotion"])
        axes[0].set_title("Promotional Demand Uplift", fontsize=13, fontweight="bold")
        axes[0].set_ylabel("Daily Units Sold")

        sns.boxplot(
            data=df,
            x="Holiday",
            y="Units_Sold",
            hue="Holiday",
            ax=axes[1],
            palette=["#94a3b8", "#f59e0b"],
            showfliers=False,
            legend=False,
        )
        axes[1].set_xticks([0, 1])
        axes[1].set_xticklabels(["Regular Day", "Holiday Season"])
        axes[1].set_title("Holiday Impact on Demand", fontsize=13, fontweight="bold")
        axes[1].set_ylabel("Daily Units Sold")

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "06_promotions_and_holidays.png"), dpi=150)
        plt.close()

        uplift_promo_pct = 0.0
        if 0 in promo_impact and 1 in promo_impact and promo_impact[0] > 0:
            uplift_promo_pct = round(((promo_impact[1] - promo_impact[0]) / promo_impact[0]) * 100, 2)

        return {
            "promo_lift_percentage": uplift_promo_pct,
            "avg_units_no_promo": round(promo_impact.get(0, 0), 2),
            "avg_units_with_promo": round(promo_impact.get(1, 0), 2),
            "avg_units_regular_day": round(holiday_impact.get(0, 0), 2),
            "avg_units_holiday": round(holiday_impact.get(1, 0), 2),
        }

    def _analyze_inventory(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyzes stockout occurrences and inventory buffer levels."""
        if "Inventory_Level" not in df.columns:
            return {"note": "Inventory_Level column not present."}

        stockout_rows = int((df["Inventory_Level"] <= 0).sum())
        total_rows = len(df)
        stockout_rate_pct = round((stockout_rows / total_rows) * 100, 2) if total_rows > 0 else 0

        # Plot Inventory Levels vs Units Sold for a representative SKU
        sample_prod = df["Product_ID"].iloc[0]
        sample_store = df["Store_ID"].iloc[0]
        sub = df[(df["Product_ID"] == sample_prod) & (df["Store_ID"] == sample_store)].tail(90)

        plt.figure(figsize=(12, 5))
        plt.plot(sub["Date"], sub["Inventory_Level"], label="Inventory Level", color="#059669", linewidth=2.0)
        plt.bar(sub["Date"], sub["Units_Sold"], label="Units Sold (Daily)", color="#ef4444", alpha=0.6)
        plt.title(f"Inventory vs Demand Dynamics (SKU: {sample_prod} at Store: {sample_store})", fontsize=14, fontweight="bold", pad=12)
        plt.xlabel("Date")
        plt.ylabel("Units / Stock")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "07_inventory_dynamics.png"), dpi=150)
        plt.close()

        return {
            "total_stockout_events": stockout_rows,
            "stockout_rate_percentage": stockout_rate_pct,
            "avg_inventory_on_hand": round(float(df["Inventory_Level"].mean()), 2),
        }
