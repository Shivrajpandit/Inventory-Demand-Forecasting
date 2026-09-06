"""
Rolling Feature Engineering
===========================
Generates strictly backward-looking rolling statistics (mean, standard deviation,
min, max) per Store and Product without lookahead bias.
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np


def generate_rolling_features(
    df: pd.DataFrame,
    target_col: str = "Units_Sold",
    group_cols: List[str] = ["Store_ID", "Product_ID"],
    windows: List[int] = [7, 14, 28],
    min_periods: int = 1,
) -> pd.DataFrame:
    """
    Computes rolling mean and standard deviation features strictly on past observations (shifted by 1).

    Args:
        df: Input DataFrame (must be sorted chronologically).
        target_col: Target demand column.
        group_cols: Partition columns.
        windows: List of rolling day windows (e.g. [7, 14, 28]).
        min_periods: Minimum number of observations required in window.

    Returns:
        DataFrame with new Rolling_Mean_{w} and Rolling_Std_{w} columns.
    """
    df_out = df.copy()
    df_out = df_out.sort_values(group_cols + ["Date"]).reset_index(drop=True)

    grouped = df_out.groupby(group_cols)[target_col]

    # Pre-shift series by 1 so the current day t is NOT included in rolling stats for day t
    shifted = grouped.shift(1)

    for w in windows:
        mean_col = f"Rolling_Mean_{w}"
        std_col = f"Rolling_Std_{w}"

        # Rolling mean and std on shifted series per group
        df_out[mean_col] = (
            df_out.groupby(group_cols)[target_col]
            .transform(lambda s: s.shift(1).rolling(window=w, min_periods=min_periods).mean())
        )
        df_out[std_col] = (
            df_out.groupby(group_cols)[target_col]
            .transform(lambda s: s.shift(1).rolling(window=w, min_periods=min_periods).std())
            .fillna(0.0)
        )

    return df_out
