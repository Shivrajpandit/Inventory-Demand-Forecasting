"""
Baseline Forecast Evaluation Runner
===================================
Runs feature engineering, performs chronological 70/15/15 train/val/test splits,
evaluates baseline models, and outputs the baseline benchmark comparison table.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import pandas as pd
from rich.console import Console
from rich.table import Table

from ml.features.feature_pipeline import FeaturePipeline
from ml.models.baselines import (
    NaivePersistenceForecast,
    SeasonalNaiveForecast,
    MovingAverageForecast,
    HistoricalMeanForecast,
)
from ml.evaluation.metrics import evaluate_forecast

console = Console()


def run_baseline_benchmarks(
    input_path: str = "data/processed/cleaned_sales_data.csv",
    output_report_path: str = "docs/baseline_evaluation.json",
):
    console.print("\n[bold cyan]1. Loading Processed Dataset...[/bold cyan]")
    df = pd.read_csv(input_path)
    console.print(f"Loaded {len(df):,} records.")

    console.print("\n[bold cyan]2. Applying Feature Pipeline (Lags + Rolling Windows)...[/bold cyan]")
    pipeline = FeaturePipeline()
    df_feat = pipeline.transform(df, drop_na=True)
    console.print(f"Engineered feature dataset: {len(df_feat):,} records with {len(df_feat.columns)} columns.")

    console.print("\n[bold cyan]3. Performing Strict Chronological Split (70/15/15)...[/bold cyan]")
    train_df, val_df, test_df = FeaturePipeline.chronological_split(df_feat, train_ratio=0.70, val_ratio=0.15)
    console.print(f"  Training Split   : {len(train_df):,} rows ({train_df['Date'].min()} to {train_df['Date'].max()})")
    console.print(f"  Validation Split : {len(val_df):,} rows ({val_df['Date'].min()} to {val_df['Date'].max()})")
    console.print(f"  Test Split       : {len(test_df):,} rows ({test_df['Date'].min()} to {test_df['Date'].max()})")

    # Fit historical mean on training set only
    hist_mean_model = HistoricalMeanForecast()
    hist_mean_model.fit(train_df)

    models = [
        NaivePersistenceForecast(),
        SeasonalNaiveForecast(),
        MovingAverageForecast(window=7),
        MovingAverageForecast(window=14),
        hist_mean_model,
    ]

    results = []
    y_test = test_df["Units_Sold"].values

    table = Table(title="Baseline Forecast Benchmark on Holdout Test Set (Real Computed Results)", header_style="bold magenta")
    table.add_column("Model Name", style="bold")
    table.add_column("MAE (Units)", justify="right")
    table.add_column("RMSE (Units)", justify="right")
    table.add_column("WAPE (%)", justify="right")
    table.add_column("sMAPE (%)", justify="right")

    for model in models:
        preds = model.predict(test_df)
        metrics = evaluate_forecast(y_test, preds)
        results.append({
            "model": model.name,
            **metrics,
        })
        table.add_row(
            model.name,
            f"{metrics['MAE']:.3f}",
            f"{metrics['RMSE']:.3f}",
            f"{metrics['WAPE_pct']:.2f}%",
            f"{metrics['sMAPE_pct']:.2f}%",
        )

    console.print("\n")
    console.print(table)

    # Save benchmark report to disk
    os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
    with open(output_report_path, "w") as f:
        json.dump(results, f, indent=2)
    console.print(f"\n[green][OK] Benchmark results saved to {output_report_path}[/green]")

    return results


if __name__ == "__main__":
    run_baseline_benchmarks()
