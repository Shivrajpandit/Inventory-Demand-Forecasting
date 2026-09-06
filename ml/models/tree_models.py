"""
Tree-Based Demand Forecasting Models
====================================
Random Forest and XGBoost Regressor wrappers with explicit feature handling and feature importances.
"""

from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb


class RandomForestDemandModel:
    """Random Forest Regressor for non-linear demand modeling."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 12,
        random_state: int = 42,
        name: str = "Random Forest",
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.name = name
        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.feature_cols: List[str] = []

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encodes categorical fields and selects numeric features."""
        df_enc = df.copy()
        for col in ["Store_ID", "Product_ID", "Category", "Season"]:
            if col in df_enc.columns:
                df_enc[col] = df_enc[col].astype("category").cat.codes
        return df_enc

    def fit(self, train_df: pd.DataFrame, target_col: str = "Units_Sold"):
        exclude = ["Date", "Product_Name", target_col]
        self.feature_cols = [c for c in train_df.columns if c not in exclude]

        df_train_prep = self._prepare_features(train_df)
        X = df_train_prep[self.feature_cols]
        y = train_df[target_col].values

        self.model.fit(X, y)
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        df_prep = self._prepare_features(df)
        preds = self.model.predict(df_prep[self.feature_cols])
        return np.clip(preds, 0, None)

    def get_feature_importance(self) -> Dict[str, float]:
        importances = self.model.feature_importances_
        imp_dict = {col: float(importances[i]) for i, col in enumerate(self.feature_cols)}
        return dict(sorted(imp_dict.items(), key=lambda x: x[1], reverse=True))


class XGBoostDemandModel:
    """XGBoost Gradient Boosted Trees for high-accuracy time-series forecasting."""

    def __init__(
        self,
        n_estimators: int = 150,
        max_depth: int = 6,
        learning_rate: float = 0.05,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42,
        name: str = "XGBoost",
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.random_state = random_state
        self.name = name

        self.model = xgb.XGBRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            random_state=self.random_state,
            n_jobs=-1,
            objective="reg:squarederror",
        )
        self.feature_cols: List[str] = []

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df_enc = df.copy()
        for col in ["Store_ID", "Product_ID", "Category", "Season"]:
            if col in df_enc.columns:
                df_enc[col] = df_enc[col].astype("category").cat.codes
        return df_enc

    def fit(
        self,
        train_df: pd.DataFrame,
        val_df: Optional[pd.DataFrame] = None,
        target_col: str = "Units_Sold",
    ):
        exclude = ["Date", "Product_Name", target_col]
        self.feature_cols = [c for c in train_df.columns if c not in exclude]

        df_train_prep = self._prepare_features(train_df)
        X_train = df_train_prep[self.feature_cols]
        y_train = train_df[target_col].values

        eval_set = None
        if val_df is not None:
            df_val_prep = self._prepare_features(val_df)
            X_val = df_val_prep[self.feature_cols]
            y_val = val_df[target_col].values
            eval_set = [(X_train, y_train), (X_val, y_val)]

        self.model.fit(X_train, y_train, eval_set=eval_set, verbose=False)
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        df_prep = self._prepare_features(df)
        preds = self.model.predict(df_prep[self.feature_cols])
        return np.clip(preds, 0, None)

    def get_feature_importance(self) -> Dict[str, float]:
        importances = self.model.feature_importances_
        imp_dict = {col: float(importances[i]) for i, col in enumerate(self.feature_cols)}
        return dict(sorted(imp_dict.items(), key=lambda x: x[1], reverse=True))
