"""
Temporal & Exogenous Feature Engineering
========================================
Generates calendar attributes, cyclical trigonometric encodings, and price elasticity features.
"""

from typing import List
import pandas as pd
import numpy as np


def generate_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates temporal calendar and cyclical features.

    Features created:
    - Day_of_Week (0-6)
    - Day_of_Month (1-31)
    - Week_of_Year (1-52)
    - Month (1-12)
    - Quarter (1-4)
    - Is_Weekend (0/1)
    - Cyclical DOW: sin_dow, cos_dow
    - Cyclical Month: sin_month, cos_month
    """
    df_out = df.copy()
    dates = pd.to_datetime(df_out["Date"])

    df_out["Day_of_Week"] = dates.dt.dayofweek
    df_out["Day_of_Month"] = dates.dt.day
    df_out["Week_of_Year"] = dates.dt.isocalendar().week.astype(int)
    df_out["Month"] = dates.dt.month
    df_out["Quarter"] = dates.dt.quarter
    df_out["Is_Weekend"] = (df_out["Day_of_Week"] >= 5).astype(int)

    # Cyclical encodings for smooth periodic transitions
    df_out["sin_dow"] = np.sin(2 * np.pi * df_out["Day_of_Week"] / 7.0)
    df_out["cos_dow"] = np.cos(2 * np.pi * df_out["Day_of_Week"] / 7.0)

    df_out["sin_month"] = np.sin(2 * np.pi * (df_out["Month"] - 1) / 12.0)
    df_out["cos_month"] = np.cos(2 * np.pi * (df_out["Month"] - 1) / 12.0)

    return df_out


def generate_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates price ratio and discount interaction features.
    """
    df_out = df.copy()
    if "Price" in df_out.columns and "Product_ID" in df_out.columns:
        # Product baseline price (median over time)
        median_price = df_out.groupby("Product_ID")["Price"].transform("median")
        df_out["Price_Ratio"] = df_out["Price"] / median_price.replace(0, 1.0)
    return df_out
