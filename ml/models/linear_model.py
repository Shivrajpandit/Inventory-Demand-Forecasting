"""
Linear Forecasting Model Wrapper
================================
Regularized Ridge Regression pipeline with categorical one-hot encoding and standard scaling.
"""

from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


class LinearDemandModel:
    """Regularized Ridge linear forecasting model."""

    def __init__(self, alpha: float = 1.0, name: str = "Ridge Regression"):
        self.alpha = alpha
        self.name = name
        self.model: Optional[Pipeline] = None
        self.feature_names: List[str] = []
        self.categorical_cols = ["Store_ID", "Category"]
        self.numeric_cols = [
            "Price", "Discount", "Promotion", "Holiday", "Is_Weekend",
            "sin_dow", "cos_dow", "sin_month", "cos_month",
            "Lag_1", "Lag_7", "Lag_14", "Lag_28",
            "Rolling_Mean_7", "Rolling_Mean_14", "Rolling_Mean_28",
            "Rolling_Std_7", "Rolling_Std_14",
        ]

    def fit(self, train_df: pd.DataFrame, target_col: str = "Units_Sold"):
        """Fits the Ridge regression pipeline on training features."""
        # Ensure available columns
        cat_cols = [c for c in self.categorical_cols if c in train_df.columns]
        num_cols = [c for c in self.numeric_cols if c in train_df.columns]

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), num_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
            ]
        )

        self.model = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", Ridge(alpha=self.alpha)),
        ])

        X = train_df[cat_cols + num_cols]
        y = train_df[target_col].values

        self.model.fit(X, y)
        self.feature_names = cat_cols + num_cols
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Generates point forecasts clipped at 0."""
        if self.model is None:
            raise ValueError("Model must be fitted before predict.")
        preds = self.model.predict(df[self.feature_names])
        return np.clip(preds, 0, None)

    def get_feature_importance(self) -> Dict[str, float]:
        """Returns normalized feature coefficient magnitudes."""
        if self.model is None:
            return {}
        regressor = self.model.named_steps["regressor"]
        preprocessor = self.model.named_steps["preprocessor"]

        # Extract encoded feature names
        encoded_cat_names = []
        if "cat" in preprocessor.named_transformers_:
            cat_encoder = preprocessor.named_transformers_["cat"]
            encoded_cat_names = list(cat_encoder.get_feature_names_out(self.categorical_cols))

        all_names = self.numeric_cols + encoded_cat_names
        coefs = np.abs(regressor.coef_)

        # Map to dict
        imp_dict = {name: float(coefs[i]) for i, name in enumerate(all_names) if i < len(coefs)}
        # Sort descending
        return dict(sorted(imp_dict.items(), key=lambda x: x[1], reverse=True))
