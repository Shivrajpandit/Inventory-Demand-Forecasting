"""
Model Training & Evaluation Orchestrator
========================================
Coordinates feature generation, model fitting, validation tuning, test evaluation,
and champion registration.
"""

import os
import json
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from ml.features.feature_pipeline import FeaturePipeline
from ml.models.baselines import (
    NaivePersistenceForecast,
    SeasonalNaiveForecast,
    MovingAverageForecast,
    HistoricalMeanForecast,
)
from ml.models.linear_model import LinearDemandModel
from ml.models.tree_models import RandomForestDemandModel, XGBoostDemandModel
from ml.models.lightgbm_model import LightGBMDemandModel
from ml.evaluation.metrics import evaluate_forecast
from ml.forecasting.registry import ModelRegistry


class ModelTrainer:
    """End-to-end model training, comparison, and evaluation pipeline."""

    def __init__(self, registry_dir: str = "models", reports_dir: str = "docs"):
        self.registry = ModelRegistry(registry_dir=registry_dir)
        self.reports_dir = reports_dir
        self.eda_reports_dir = os.path.join(reports_dir, "eda_reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.eda_reports_dir, exist_ok=True)

    def run_training_pipeline(
        self,
        data_path: str = "data/processed/cleaned_sales_data.csv",
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Executes full model comparison pipeline:
        1. Feature engineering
        2. 70/15/15 chronological split
        3. Train baselines, Ridge, Random Forest, LightGBM, XGBoost
        4. Evaluate on holdout test set
        5. Select and register champion model
        """
        print("1. Loading dataset and building feature store...")
        df = pd.read_csv(data_path)
        pipeline = FeaturePipeline()
        df_feat = pipeline.transform(df, drop_na=True)

        print("2. Chronologically partitioning dataset (70% Train / 15% Val / 15% Test)...")
        train_df, val_df, test_df = FeaturePipeline.chronological_split(df_feat, train_ratio=0.70, val_ratio=0.15)
        y_test = test_df["Units_Sold"].values

        print(f"   Train: {len(train_df):,} | Val: {len(val_df):,} | Test: {len(test_df):,}")

        # Baseline: Historical Mean
        hist_mean = HistoricalMeanForecast()
        hist_mean.fit(train_df)

        # Candidate Models
        models_to_train = [
            ("Naive (Lag 1)", NaivePersistenceForecast(), {}),
            ("Moving Average (14d)", MovingAverageForecast(window=14), {}),
            ("Product Historical Mean", hist_mean, {}),
            ("Ridge Regression", LinearDemandModel(alpha=10.0), {"alpha": 10.0}),
            ("Random Forest", RandomForestDemandModel(n_estimators=100, max_depth=10), {"n_estimators": 100, "max_depth": 10}),
            ("LightGBM", LightGBMDemandModel(n_estimators=150, learning_rate=0.05, num_leaves=31), {"n_estimators": 150, "learning_rate": 0.05, "num_leaves": 31}),
            ("XGBoost", XGBoostDemandModel(n_estimators=150, max_depth=6, learning_rate=0.05), {"n_estimators": 150, "max_depth": 6, "learning_rate": 0.05}),
        ]

        results = []
        trained_instances = {}
        predictions_map = {}

        print("3. Training and evaluating models...")
        for name, model, params in models_to_train:
            print(f"   Fitting {name}...")
            if hasattr(model, "fit"):
                if isinstance(model, (XGBoostDemandModel, LightGBMDemandModel)):
                    model.fit(train_df, val_df=val_df)
                elif not isinstance(model, HistoricalMeanForecast):
                    model.fit(train_df)

            # Predict on holdout test partition
            preds = model.predict(test_df)
            metrics = evaluate_forecast(y_test, preds)
            predictions_map[name] = preds

            imp = {}
            if hasattr(model, "get_feature_importance"):
                imp = model.get_feature_importance()

            results.append({
                "Model": name,
                "MAE": metrics["MAE"],
                "RMSE": metrics["RMSE"],
                "WAPE_pct": metrics["WAPE_pct"],
                "sMAPE_pct": metrics["sMAPE_pct"],
                "params": params,
                "importances": imp,
            })
            trained_instances[name] = (model, params, imp, metrics)

        comparison_df = pd.DataFrame(results).sort_values(by="MAE").reset_index(drop=True)

        # 4. Identify Champion Model (Lowest MAE / WAPE)
        champion_row = comparison_df.iloc[0]
        champion_name = champion_row["Model"]
        print(f"\n[CHAMPION] Champion Model Selected: {champion_name} (MAE: {champion_row['MAE']:.3f}, WAPE: {champion_row['WAPE_pct']}%)")

        # 5. Persist all ML models and register Champion
        for name, (model_obj, params, imp, metrics) in trained_instances.items():
            if hasattr(model_obj, "fit") and not isinstance(model_obj, HistoricalMeanForecast):
                is_champ = (name == champion_name)
                self.registry.save_model(
                    model_obj=model_obj,
                    model_name=name,
                    metrics=metrics,
                    hyperparameters=params,
                    feature_importance=imp,
                    version="1.0.0",
                    is_champion=is_champ,
                )

        # 6. Save Comparison JSON
        comparison_json_path = os.path.join(self.reports_dir, "model_comparison.json")
        with open(comparison_json_path, "w") as f:
            json.dump(results, f, indent=2)

        # 7. Generate Actual vs Predicted Plot for Champion
        self._plot_actual_vs_predicted(test_df, y_test, predictions_map[champion_name], champion_name)

        return comparison_df, results[0]

    def _plot_actual_vs_predicted(
        self,
        test_df: pd.DataFrame,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        model_name: str,
    ):
        """Plots aggregate and SKU-level actual vs predicted demand curves."""
        plot_df = test_df[["Date", "Store_ID", "Product_ID", "Product_Name"]].copy()
        plot_df["Actual"] = y_true
        plot_df["Predicted"] = y_pred
        plot_df["Date"] = pd.to_datetime(plot_df["Date"])

        # Aggregate daily total
        daily_agg = plot_df.groupby("Date")[["Actual", "Predicted"]].sum()

        fig, axes = plt.subplots(2, 1, figsize=(14, 10))

        # 1. Total Daily System Demand
        axes[0].plot(daily_agg.index, daily_agg["Actual"], label="Actual Total Demand", color="#1e293b", linewidth=1.8)
        axes[0].plot(daily_agg.index, daily_agg["Predicted"], label=f"Predicted ({model_name})", color="#2563eb", linestyle="--", linewidth=1.8)
        axes[0].set_title(f"Holdout Test: Total System Demand - Actual vs {model_name}", fontsize=13, fontweight="bold")
        axes[0].set_ylabel("Total Units Sold")
        axes[0].legend()

        # 2. Sample SKU Demand
        sample_prod = test_df["Product_Name"].iloc[0]
        sample_store = test_df["Store_ID"].iloc[0]
        sku_sub = plot_df[(plot_df["Product_Name"] == sample_prod) & (plot_df["Store_ID"] == sample_store)].tail(45)

        axes[1].plot(sku_sub["Date"], sku_sub["Actual"], label=f"Actual ({sample_prod})", color="#059669", marker="o", linewidth=1.5)
        axes[1].plot(sku_sub["Date"], sku_sub["Predicted"], label=f"Predicted ({model_name})", color="#ea580c", linestyle="--", marker="s", linewidth=1.5)
        axes[1].set_title(f"Holdout Test: SKU Level Demand - {sample_prod} at {sample_store}", fontsize=13, fontweight="bold")
        axes[1].set_ylabel("Daily Units Sold")
        axes[1].legend()

        plt.tight_layout()
        out_plot_path = os.path.join(self.eda_reports_dir, "08_actual_vs_predicted.png")
        plt.savefig(out_plot_path, dpi=150)
        plt.close()
        print(f"Actual vs Predicted evaluation plot saved to: {out_plot_path}")
