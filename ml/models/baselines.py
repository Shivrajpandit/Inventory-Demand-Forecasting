"""
Baseline Forecasting Models
===========================
Defines deterministic and statistical baseline models to establish performance benchmarks.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from ml.evaluation.metrics import evaluate_forecast


class NaivePersistenceForecast:
    """Predicts future demand using the most recent known observation (Lag 1)."""

    def __init__(self, name: str = "Naive (Lag 1)"):
        self.name = name

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if "Lag_1" in df.columns:
            return df["Lag_1"].fillna(0).values
        raise ValueError("DataFrame must contain 'Lag_1' feature.")


class SeasonalNaiveForecast:
    """Predicts future demand using the same day of the prior week (Lag 7)."""

    def __init__(self, name: str = "Seasonal Naive (Lag 7)"):
        self.name = name

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if "Lag_7" in df.columns:
            return df["Lag_7"].fillna(0).values
        raise ValueError("DataFrame must contain 'Lag_7' feature.")


class MovingAverageForecast:
    """Predicts future demand using rolling historical mean (7-day or 14-day)."""

    def __init__(self, window: int = 7, name: Optional[str] = None):
        self.window = window
        self.name = name or f"Moving Average ({window}d)"

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        col = f"Rolling_Mean_{self.window}"
        if col in df.columns:
            return df[col].fillna(0).values
        raise ValueError(f"DataFrame must contain '{col}' feature.")


class HistoricalMeanForecast:
    """Predicts demand using product-level historical average."""

    def __init__(self, name: str = "Product Historical Mean"):
        self.name = name
        self.means: Dict[str, float] = {}
        self.global_mean: float = 0.0

    def fit(self, train_df: pd.DataFrame, target_col: str = "Units_Sold"):
        self.means = train_df.groupby("Product_ID")[target_col].mean().to_dict()
        self.global_mean = float(train_df[target_col].mean())

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        return df["Product_ID"].map(self.means).fillna(self.global_mean).values
