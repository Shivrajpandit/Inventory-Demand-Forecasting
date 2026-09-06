"""
Feature Pipeline & Chronological Splitter
=========================================
Unifies all feature extraction steps and implements strict chronological data splitting.
"""

from typing import Tuple, List, Optional
import pandas as pd
import numpy as np

from ml.features.lag_features import generate_lag_features
from ml.features.rolling_features import generate_rolling_features
from ml.features.temporal_features import generate_temporal_features, generate_price_features


class FeaturePipeline:
    """End-to-end feature engineering pipeline for tabular demand forecasting."""

    def __init__(
        self,
        lags: List[int] = [1, 7, 14, 28],
        rolling_windows: List[int] = [7, 14, 28],
        target_col: str = "Units_Sold",
    ):
        self.lags = lags
        self.rolling_windows = rolling_windows
        self.target_col = target_col

    def transform(self, df: pd.DataFrame, drop_na: bool = True) -> pd.DataFrame:
        """
        Applies lag, rolling, temporal, and price feature transformations.

        Args:
            df: Cleaned sales DataFrame.
            drop_na: Whether to drop initial warm-up rows containing NaN lags.

        Returns:
            Engineered feature DataFrame.
        """
        df_feat = df.copy()

        # 1. Temporal & Cyclical Features
        df_feat = generate_temporal_features(df_feat)

        # 2. Price Features
        df_feat = generate_price_features(df_feat)

        # 3. Auto-regressive Lag Features
        df_feat = generate_lag_features(
            df_feat,
            target_col=self.target_col,
            group_cols=["Store_ID", "Product_ID"],
            lags=self.lags,
        )

        # 4. Backward-Looking Rolling Statistics
        df_feat = generate_rolling_features(
            df_feat,
            target_col=self.target_col,
            group_cols=["Store_ID", "Product_ID"],
            windows=self.rolling_windows,
        )

        if drop_na:
            # Drop rows where largest lag is NaN (warm-up period)
            max_lag = max(self.lags)
            df_feat = df_feat.dropna(subset=[f"Lag_{max_lag}"]).reset_index(drop=True)

        return df_feat

    @staticmethod
    def chronological_split(
        df: pd.DataFrame,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        date_col: str = "Date",
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Splits data chronologically into Train (70%), Validation (15%), and Test (15%) partitions.

        Args:
            df: Feature DataFrame.
            train_ratio: Proportion for training.
            val_ratio: Proportion for validation.
            date_col: Date column for time ordering.

        Returns:
            Tuple of (train_df, val_df, test_df).
        """
        df_sorted = df.sort_values(date_col).reset_index(drop=True)
        unique_dates = df_sorted[date_col].drop_duplicates().sort_values().values

        n_dates = len(unique_dates)
        train_end_idx = int(n_dates * train_ratio)
        val_end_idx = int(n_dates * (train_ratio + val_ratio))

        train_cutoff = unique_dates[train_end_idx]
        val_cutoff = unique_dates[val_end_idx]

        train_df = df_sorted[df_sorted[date_col] < train_cutoff].reset_index(drop=True)
        val_df = df_sorted[(df_sorted[date_col] >= train_cutoff) & (df_sorted[date_col] < val_cutoff)].reset_index(drop=True)
        test_df = df_sorted[df_sorted[date_col] >= val_cutoff].reset_index(drop=True)

        return train_df, val_df, test_df
