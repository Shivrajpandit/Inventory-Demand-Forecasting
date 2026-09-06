"""
Lag Feature Engineering
=======================
Generates backward-looking auto-regressive lag features per Store and Product.
Ensures zero data leakage by computing shifts strictly on historical values.
"""

from typing import List
import pandas as pd


def generate_lag_features(
    df: pd.DataFrame,
    target_col: str = "Units_Sold",
    group_cols: List[str] = ["Store_ID", "Product_ID"],
    lags: List[int] = [1, 7, 14, 28],
) -> pd.DataFrame:
    """
    Computes lag features for the specified target column partitioned by group_cols.

    Args:
        df: Input DataFrame (must be sorted chronologically).
        target_col: Target demand column to lag.
        group_cols: Partition columns (e.g., Store_ID, Product_ID).
        lags: List of day offsets to compute (e.g. [1, 7, 14, 28]).

    Returns:
        DataFrame with new Lag_{k} columns.
    """
    df_out = df.copy()

    # Ensure chronological sort before shifting
    df_out = df_out.sort_values(group_cols + ["Date"]).reset_index(drop=True)

    for lag in lags:
        col_name = f"Lag_{lag}"
        df_out[col_name] = (
            df_out.groupby(group_cols)[target_col]
            .shift(lag)
        )

    return df_out
