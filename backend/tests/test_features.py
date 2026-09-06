"""
Unit Tests for Feature Engineering & No Data Leakage
====================================================
"""

import pytest
import pandas as pd
import numpy as np
from ml.features.lag_features import generate_lag_features
from ml.features.rolling_features import generate_rolling_features
from ml.features.temporal_features import generate_temporal_features
from ml.features.feature_pipeline import FeaturePipeline


def test_lag_features_no_leakage():
    """Validates that Lag_1 on day t equals the exact value of Units_Sold on day t-1."""
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "Store_ID": ["S1", "S1", "S1", "S1"],
        "Product_ID": ["P1", "P1", "P1", "P1"],
        "Units_Sold": [10, 20, 30, 40],
    }
    df = pd.DataFrame(data)
    df_lag = generate_lag_features(df, lags=[1, 2])

    # Day 1: Lags must be NaN
    assert pd.isna(df_lag.loc[0, "Lag_1"])
    assert pd.isna(df_lag.loc[0, "Lag_2"])

    # Day 2: Lag_1 must be 10, Lag_2 must be NaN
    assert df_lag.loc[1, "Lag_1"] == 10
    assert pd.isna(df_lag.loc[1, "Lag_2"])

    # Day 3: Lag_1 must be 20, Lag_2 must be 10
    assert df_lag.loc[2, "Lag_1"] == 20
    assert df_lag.loc[2, "Lag_2"] == 10

    # Day 4: Lag_1 must be 30, Lag_2 must be 20
    assert df_lag.loc[3, "Lag_1"] == 30
    assert df_lag.loc[3, "Lag_2"] == 20


def test_rolling_features_shift_prevents_leakage():
    """Validates that Rolling_Mean_3 on day t does NOT include day t Units_Sold."""
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "Store_ID": ["S1", "S1", "S1", "S1"],
        "Product_ID": ["P1", "P1", "P1", "P1"],
        "Units_Sold": [10, 20, 30, 100],  # Massive spike on Day 4
    }
    df = pd.DataFrame(data)
    df_roll = generate_rolling_features(df, windows=[3])

    # Day 4: Rolling_Mean_3 should be average of days 1, 2, 3 -> (10 + 20 + 30) / 3 = 20.0
    # If day 4 was leaked, it would be (20 + 30 + 100) / 3 = 50.0
    assert df_roll.loc[3, "Rolling_Mean_3"] == 20.0


def test_chronological_split_boundaries():
    """Validates that train, validation, and test splits strictly follow chronological order without overlap."""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    df = pd.DataFrame({
        "Date": dates.strftime("%Y-%m-%d"),
        "Store_ID": ["S1"] * 100,
        "Product_ID": ["P1"] * 100,
        "Units_Sold": np.arange(100),
    })

    train, val, test = FeaturePipeline.chronological_split(df, train_ratio=0.70, val_ratio=0.15)

    assert len(train) == 70
    assert len(val) == 15
    assert len(test) == 15

    # Max train date must be strictly less than min val date
    assert train["Date"].max() < val["Date"].min()
    # Max val date must be strictly less than min test date
    assert val["Date"].max() < test["Date"].min()
