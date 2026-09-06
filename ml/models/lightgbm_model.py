"""
LightGBM Demand Forecasting Model
=================================
Fast, gradient boosted decision tree forecasting model with native categorical feature support.
"""

from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
import lightgbm as lgb


class LightGBMDemandModel:
    """LightGBM Regressor for demand forecasting."""

    def __init__(
        self,
        n_estimators: int = 150,
        learning_rate: float = 0.05,
        num_leaves: int = 31,
        random_state: int = 42,
        name: str = "LightGBM",
    ):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.num_leaves = num_leaves
        self.random_state = random_state
        self.name = name

        self.model = lgb.LGBMRegressor(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            num_leaves=self.num_leaves,
            random_state=self.random_state,
            n_jobs=-1,
            verbosity=-1,
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
            eval_set = [(X_val, y_val)]

        self.model.fit(X_train, y_train, eval_set=eval_set)
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        df_prep = self._prepare_features(df)
        preds = self.model.predict(df_prep[self.feature_cols])
        return np.clip(preds, 0, None)

    def get_feature_importance(self) -> Dict[str, float]:
        importances = self.model.feature_importances_
        # Normalize to percentage
        total = np.sum(importances)
        if total > 0:
            norm_imp = importances / total
        else:
            norm_imp = importances
        imp_dict = {col: float(norm_imp[i]) for i, col in enumerate(self.feature_cols)}
        return dict(sorted(imp_dict.items(), key=lambda x: x[1], reverse=True))
