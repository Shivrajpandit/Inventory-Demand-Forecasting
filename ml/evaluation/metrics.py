"""
Time-Series Evaluation Metrics
==============================
Implements standardized evaluation metrics: MAE, RMSE, WAPE, and sMAPE.
"""

from typing import Dict, Union
import numpy as np
import pandas as pd


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Computes Mean Absolute Error (MAE)."""
    return float(np.mean(np.abs(y_true - y_pred)))


def root_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Computes Root Mean Squared Error (RMSE)."""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def weighted_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Computes Weighted Absolute Percentage Error (WAPE).
    WAPE = sum(|y - y_hat|) / sum(y) * 100%
    Robust to zero-demand observations.
    """
    denom = np.sum(y_true)
    if denom == 0:
        return 0.0
    return float((np.sum(np.abs(y_true - y_pred)) / denom) * 100.0)


def symmetric_mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Computes Symmetric Mean Absolute Percentage Error (sMAPE).
    Bound between 0% and 200%.
    """
    denom = (np.abs(y_true) + np.abs(y_pred))
    # Handle both y_true and y_pred being 0
    zero_mask = denom == 0
    smape_elements = np.zeros_like(y_true, dtype=float)
    smape_elements[~zero_mask] = (2.0 * np.abs(y_true[~zero_mask] - y_pred[~zero_mask])) / denom[~zero_mask]
    return float(np.mean(smape_elements) * 100.0)


def evaluate_forecast(
    y_true: Union[np.ndarray, pd.Series],
    y_pred: Union[np.ndarray, pd.Series],
) -> Dict[str, float]:
    """
    Calculates all core forecasting metrics across actuals and predictions.
    """
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)

    # Predictions cannot be negative in physical inventory
    yp = np.clip(yp, 0, None)

    return {
        "MAE": round(mean_absolute_error(yt, yp), 3),
        "RMSE": round(root_mean_squared_error(yt, yp), 3),
        "WAPE_pct": round(weighted_absolute_percentage_error(yt, yp), 2),
        "sMAPE_pct": round(symmetric_mean_absolute_percentage_error(yt, yp), 2),
    }
