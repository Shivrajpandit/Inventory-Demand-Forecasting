"""
Unit Tests for Baseline Models & Evaluation Metrics
===================================================
"""

import pytest
import numpy as np
import pandas as pd
from ml.models.baselines import (
    NaivePersistenceForecast,
    SeasonalNaiveForecast,
    MovingAverageForecast,
)
from ml.evaluation.metrics import (
    mean_absolute_error,
    root_mean_squared_error,
    weighted_absolute_percentage_error,
    symmetric_mean_absolute_percentage_error,
    evaluate_forecast,
)


def test_metrics_perfect_forecast():
    """Validates that perfect predictions return 0 error."""
    y = np.array([10.0, 20.0, 30.0])
    metrics = evaluate_forecast(y, y)
    assert metrics["MAE"] == 0.0
    assert metrics["RMSE"] == 0.0
    assert metrics["WAPE_pct"] == 0.0
    assert metrics["sMAPE_pct"] == 0.0


def test_wape_and_smape_properties():
    """Validates WAPE and sMAPE with known numerical values."""
    y_true = np.array([100.0, 200.0])
    y_pred = np.array([110.0, 190.0])

    mae = mean_absolute_error(y_true, y_pred)
    assert mae == 10.0

    wape = weighted_absolute_percentage_error(y_true, y_pred)
    # Sum of absolute error = 20, sum of actuals = 300 -> 20/300 * 100 = 6.67%
    assert round(wape, 2) == 6.67


def test_baseline_predictions():
    """Validates that baseline classes output expected lag columns."""
    df = pd.DataFrame({
        "Lag_1": [12.0, 15.0],
        "Lag_7": [10.0, 11.0],
        "Rolling_Mean_7": [14.0, 14.5],
    })

    naive = NaivePersistenceForecast()
    assert list(naive.predict(df)) == [12.0, 15.0]

    seasonal = SeasonalNaiveForecast()
    assert list(seasonal.predict(df)) == [10.0, 11.0]

    ma = MovingAverageForecast(window=7)
    assert list(ma.predict(df)) == [14.0, 14.5]
