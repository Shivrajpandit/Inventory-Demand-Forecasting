"""
Unit Tests for Machine Learning Models & Training Pipeline
==========================================================
"""

import os
import pytest
import numpy as np
import pandas as pd

from ml.features.feature_pipeline import FeaturePipeline
from ml.models.linear_model import LinearDemandModel
from ml.models.tree_models import RandomForestDemandModel, XGBoostDemandModel
from ml.models.lightgbm_model import LightGBMDemandModel
from ml.forecasting.registry import ModelRegistry


@pytest.fixture
def sample_features_df():
    """Generates small synthetic features dataset."""
    dates = pd.date_range("2024-01-01", periods=60, freq="D")
    records = []
    for d in dates:
        for s in ["STR_01", "STR_02"]:
            for p in ["PRD_01", "PRD_02"]:
                records.append({
                    "Date": d.strftime("%Y-%m-%d"),
                    "Store_ID": s,
                    "Product_ID": p,
                    "Product_Name": f"Product {p}",
                    "Category": "Dairy",
                    "Units_Sold": int(np.random.randint(5, 50)),
                    "Price": 4.99,
                    "Discount": 0.0,
                    "Promotion": 0,
                    "Holiday": 0,
                    "Day_of_Week": d.weekday(),
                    "Month": d.month,
                    "Season": "Winter",
                    "Inventory_Level": 100,
                })
    df = pd.DataFrame(records)
    pipeline = FeaturePipeline()
    return pipeline.transform(df, drop_na=True)


def test_linear_model_fit_predict(sample_features_df):
    """Validates Linear/Ridge model fitting, prediction bounds, and feature importance."""
    train_df, val_df, test_df = FeaturePipeline.chronological_split(sample_features_df, 0.7, 0.15)
    model = LinearDemandModel(alpha=1.0)
    model.fit(train_df)

    preds = model.predict(test_df)
    assert len(preds) == len(test_df)
    assert (preds >= 0).all()  # No negative demand

    imp = model.get_feature_importance()
    assert len(imp) > 0


def test_tree_models_fit_predict(sample_features_df):
    """Validates Random Forest, XGBoost, and LightGBM models."""
    train_df, val_df, test_df = FeaturePipeline.chronological_split(sample_features_df, 0.7, 0.15)

    rf = RandomForestDemandModel(n_estimators=10, max_depth=4)
    rf.fit(train_df)
    rf_preds = rf.predict(test_df)
    assert len(rf_preds) == len(test_df)
    assert len(rf.get_feature_importance()) > 0

    xgb = XGBoostDemandModel(n_estimators=10, max_depth=3)
    xgb.fit(train_df, val_df=val_df)
    xgb_preds = xgb.predict(test_df)
    assert len(xgb_preds) == len(test_df)
    assert len(xgb.get_feature_importance()) > 0

    lgb = LightGBMDemandModel(n_estimators=10, num_leaves=7)
    lgb.fit(train_df, val_df=val_df)
    lgb_preds = lgb.predict(test_df)
    assert len(lgb_preds) == len(test_df)
    assert len(lgb.get_feature_importance()) > 0


def test_model_registry(tmp_path):
    """Validates saving and loading from model registry."""
    reg_dir = str(tmp_path / "models")
    registry = ModelRegistry(registry_dir=reg_dir)

    dummy_model = {"weights": [1, 2, 3]}
    metrics = {"MAE": 2.5, "RMSE": 3.1, "WAPE_pct": 12.4, "sMAPE_pct": 11.2}
    imp = {"Lag_1": 0.5, "Lag_7": 0.3}

    registry.save_model(
        model_obj=dummy_model,
        model_name="Test Model",
        metrics=metrics,
        hyperparameters={"alpha": 1.0},
        feature_importance=imp,
        is_champion=True,
    )

    loaded = registry.load_champion_model()
    assert loaded["weights"] == [1, 2, 3]

    meta = registry.load_champion_metadata()
    assert meta["model_name"] == "Test Model"
    assert meta["metrics"]["MAE"] == 2.5
