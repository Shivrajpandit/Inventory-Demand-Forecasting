"""
Unit Tests for Data Cleaning & Grid Completion
==============================================
"""

import pytest
import pandas as pd
import numpy as np
from ml.preprocessing.cleaner import DataCleaner


def test_cleaner_clips_negative_sales():
    """Validates that negative sales are safely clipped to zero."""
    data = {
        "Date": ["2024-01-01", "2024-01-02"],
        "Product_ID": ["PRD_01", "PRD_01"],
        "Product_Name": ["Milk", "Milk"],
        "Category": ["Dairy", "Dairy"],
        "Store_ID": ["STR_01", "STR_01"],
        "Units_Sold": [-10, 25],
        "Price": [4.99, 4.99],
    }
    df = pd.DataFrame(data)
    cleaner = DataCleaner(complete_date_grid=False)
    cleaned = cleaner.clean(df)

    assert (cleaned["Units_Sold"] >= 0).all()
    assert cleaned.loc[cleaned["Date"] == "2024-01-01", "Units_Sold"].iloc[0] == 0


def test_cleaner_completes_date_grid():
    """Validates that missing calendar days in time series are padded with 0 sales."""
    data = {
        # Day 2024-01-02 is missing
        "Date": ["2024-01-01", "2024-01-03"],
        "Product_ID": ["PRD_01", "PRD_01"],
        "Product_Name": ["Milk", "Milk"],
        "Category": ["Dairy", "Dairy"],
        "Store_ID": ["STR_01", "STR_01"],
        "Units_Sold": [10, 20],
        "Price": [4.99, 4.99],
    }
    df = pd.DataFrame(data)
    cleaner = DataCleaner(complete_date_grid=True)
    cleaned = cleaner.clean(df)

    # Must now have 3 rows for the 3 dates
    assert len(cleaned) == 3
    dates = cleaned["Date"].dt.strftime("%Y-%m-%d").tolist()
    assert "2024-01-02" in dates
    padded_row = cleaned[cleaned["Date"] == "2024-01-02"].iloc[0]
    assert padded_row["Units_Sold"] == 0
    assert padded_row["Price"] == 4.99


def test_cleaner_deduplicates_same_day_transactions():
    """Validates multiple transactions within the same day are aggregated."""
    data = {
        "Date": ["2024-01-01", "2024-01-01"],
        "Product_ID": ["PRD_01", "PRD_01"],
        "Product_Name": ["Milk", "Milk"],
        "Category": ["Dairy", "Dairy"],
        "Store_ID": ["STR_01", "STR_01"],
        "Units_Sold": [10, 15],
        "Price": [4.99, 4.99],
    }
    df = pd.DataFrame(data)
    cleaner = DataCleaner(complete_date_grid=False, remove_duplicates=True)
    cleaned = cleaner.clean(df)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["Units_Sold"] == 25
