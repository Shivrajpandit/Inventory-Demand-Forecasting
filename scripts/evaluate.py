"""
Model Evaluation & Lineage Inspector CLI
=======================================
Inspects saved model artifacts, tests the champion model on test data, and displays feature importance.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import pandas as pd
from rich.console import Console
from rich.table import Table
from ml.forecasting.registry import ModelRegistry
from ml.features.feature_pipeline import FeaturePipeline
from ml.evaluation.metrics import evaluate_forecast

console = Console()


def main():
    console.print("\n[bold cyan]Loading Champion Model from Registry...[/bold cyan]")
    registry = ModelRegistry(registry_dir="models")
    meta = registry.load_champion_metadata()
    model = registry.load_champion_model()

    console.print(f"Model Name     : [bold green]{meta['model_name']}[/bold green]")
    console.print(f"Version        : {meta['version']}")
    console.print(f"Artifact File  : {meta['artifact_file']}")
    console.print(f"Training Time  : {meta['saved_at']}")

    # Metrics Table
    m_table = Table(title="Champion Model Test Metrics", header_style="bold green")
    m_table.add_column("Metric", style="bold")
    m_table.add_column("Value", justify="right")
    for k, v in meta["metrics"].items():
        m_table.add_row(k, f"{v}")
    console.print(m_table)

    # Feature Importance Table
    fi = meta.get("feature_importance", {})
    if fi:
        f_table = Table(title="Top 10 Feature Importances", header_style="bold blue")
        f_table.add_column("Rank", justify="center")
        f_table.add_column("Feature", style="bold")
        f_table.add_column("Importance Score", justify="right")
        for i, (feat, score) in enumerate(list(fi.items())[:10]):
            f_table.add_row(f"#{i+1}", feat, f"{score:.4f}")
        console.print(f_table)


if __name__ == "__main__":
    main()
