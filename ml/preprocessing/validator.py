"""
Data Validation Module
======================
Validates raw retail sales data for required columns, data types, value ranges,
and structural consistency before preprocessing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np


REQUIRED_COLUMNS = [
    "Date",
    "Product_ID",
    "Product_Name",
    "Category",
    "Store_ID",
    "Units_Sold",
    "Price",
]

OPTIONAL_COLUMNS = [
    "Discount",
    "Promotion",
    "Holiday",
    "Day_of_Week",
    "Month",
    "Season",
    "Inventory_Level",
]


@dataclass
class ValidationReport:
    """Stores the outcome and detailed findings of data validation."""
    is_valid: bool
    total_rows: int = 0
    total_columns: int = 0
    missing_required_columns: List[str] = field(default_factory=list)
    missing_values_per_column: Dict[str, int] = field(default_factory=dict)
    duplicate_rows_count: int = 0
    negative_sales_count: int = 0
    negative_price_count: int = 0
    invalid_dates_count: int = 0
    date_range: Optional[Tuple[str, str]] = None
    unique_stores_count: int = 0
    unique_products_count: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        """Returns a formatted human-readable summary of validation results."""
        status = "PASSED" if self.is_valid else "FAILED"
        lines = [
            f"--- Data Validation Report: [{status}] ---",
            f"Total Records: {self.total_rows:,} | Columns: {self.total_columns}",
            f"Date Range: {self.date_range[0] if self.date_range else 'N/A'} to {self.date_range[1] if self.date_range else 'N/A'}",
            f"Unique Stores: {self.unique_stores_count} | Unique SKUs: {self.unique_products_count}",
            f"Duplicate Records: {self.duplicate_rows_count:,}",
            f"Negative Sales Rows: {self.negative_sales_count:,}",
            f"Negative/Zero Price Rows: {self.negative_price_count:,}",
            f"Invalid Dates: {self.invalid_dates_count:,}",
        ]
        if self.errors:
            lines.append("Errors:")
            for err in self.errors:
                lines.append(f"  ❌ {err}")
        if self.warnings:
            lines.append("Warnings:")
            for warn in self.warnings:
                lines.append(f"  ⚠️ {warn}")
        return "\n".join(lines)


class DataValidator:
    """Validates raw and ingested retail sales datasets."""

    def __init__(self, required_columns: Optional[List[str]] = None):
        self.required_columns = required_columns or REQUIRED_COLUMNS

    def validate(self, df: pd.DataFrame) -> ValidationReport:
        """Runs validation checks across the given DataFrame."""
        report = ValidationReport(is_valid=True, total_rows=len(df), total_columns=len(df.columns))

        # Check required columns
        missing_cols = [col for col in self.required_columns if col not in df.columns]
        if missing_cols:
            report.is_valid = False
            report.missing_required_columns = missing_cols
            report.errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return report

        # Check missing values
        null_counts = df.isnull().sum()
        report.missing_values_per_column = {col: int(cnt) for col, cnt in null_counts.items() if cnt > 0}
        if report.missing_values_per_column:
            report.warnings.append(
                f"Missing values detected in: {', '.join([f'{k} ({v})' for k, v in report.missing_values_per_column.items()])}"
            )

        # Check duplicate rows (Store_ID + Product_ID + Date)
        if "Date" in df.columns and "Store_ID" in df.columns and "Product_ID" in df.columns:
            duplicates = df.duplicated(subset=["Store_ID", "Product_ID", "Date"]).sum()
            report.duplicate_rows_count = int(duplicates)
            if duplicates > 0:
                report.warnings.append(f"Found {duplicates} duplicate (Store, Product, Date) entries.")

        # Check Date column validity
        if "Date" in df.columns:
            date_series = pd.to_datetime(df["Date"], errors="coerce")
            invalid_dates = int(date_series.isna().sum())
            report.invalid_dates_count = invalid_dates
            if invalid_dates > 0:
                report.is_valid = False
                report.errors.append(f"Found {invalid_dates} unparseable / invalid date entries.")
            else:
                report.date_range = (
                    date_series.min().strftime("%Y-%m-%d"),
                    date_series.max().strftime("%Y-%m-%d"),
                )

        # Check Negative Sales
        if "Units_Sold" in df.columns:
            numeric_sales = pd.to_numeric(df["Units_Sold"], errors="coerce")
            neg_sales = int((numeric_sales < 0).sum())
            report.negative_sales_count = neg_sales
            if neg_sales > 0:
                report.warnings.append(f"Found {neg_sales} negative sales values (returns/anomalies).")

        # Check Price
        if "Price" in df.columns:
            numeric_price = pd.to_numeric(df["Price"], errors="coerce")
            neg_price = int((numeric_price <= 0).sum())
            report.negative_price_count = neg_price
            if neg_price > 0:
                report.warnings.append(f"Found {neg_price} zero or negative price entries.")

        # Entity Counts
        if "Store_ID" in df.columns:
            report.unique_stores_count = int(df["Store_ID"].nunique())
        if "Product_ID" in df.columns:
            report.unique_products_count = int(df["Product_ID"].nunique())

        return report
