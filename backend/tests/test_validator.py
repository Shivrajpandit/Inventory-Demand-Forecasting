"""
Unit Tests for Data Validation & Schema Enforcement
===================================================
"""

import pytest
import pandas as pd
from ml.preprocessing.validator import DataValidator, REQUIRED_COLUMNS


def test_validator_with_valid_data():
    """Validates that a correctly formatted DataFrame passes validation."""
    data = {
        "Date": ["2024-01-01", "2024-01-02"],
        "Product_ID": ["PRD_01", "PRD_01"],
        "Product_Name": ["Milk", "Milk"],
        "Category": ["Dairy", "Dairy"],
        "Store_ID": ["STR_01", "STR_01"],
        "Units_Sold": [10, 15],
        "Price": [4.99, 4.99],
    }
    df = pd.DataFrame(data)
    validator = DataValidator()
    report = validator.validate(df)

    assert report.is_valid is True
    assert len(report.errors) == 0
    assert report.total_rows == 2
    assert report.unique_stores_count == 1
    assert report.unique_products_count == 1


def test_validator_missing_required_column():
    """Validates that missing essential columns trigger validation failure."""
    data = {
        "Date": ["2024-01-01"],
        "Product_ID": ["PRD_01"],
        # Missing Units_Sold and Price
    }
    df = pd.DataFrame(data)
    validator = DataValidator()
    report = validator.validate(df)

    assert report.is_valid is False
    assert "Units_Sold" in report.missing_required_columns
    assert "Price" in report.missing_required_columns
    assert len(report.errors) > 0


def test_validator_detects_negative_values():
    """Validates that negative sales and prices are logged in the report."""
    data = {
        "Date": ["2024-01-01", "2024-01-02"],
        "Product_ID": ["PRD_01", "PRD_01"],
        "Product_Name": ["Milk", "Milk"],
        "Category": ["Dairy", "Dairy"],
        "Store_ID": ["STR_01", "STR_01"],
        "Units_Sold": [-5, 20],  # Negative sale
        "Price": [4.99, -1.0],   # Negative price
    }
    df = pd.DataFrame(data)
    validator = DataValidator()
    report = validator.validate(df)

    assert report.negative_sales_count == 1
    assert report.negative_price_count == 1
