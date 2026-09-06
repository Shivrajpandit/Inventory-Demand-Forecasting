"""
Master Model Training & Registration CLI
=======================================
Executes feature building, multi-model training, holdout evaluation,
and saves the champion model to the model registry.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rich.console import Console
from rich.table import Table
from ml.forecasting.trainer import ModelTrainer

console = Console()


def main():
    console.print("[bold blue]================================================================[/bold blue]")
    console.print("[bold cyan]  AI-Powered Inventory Demand Forecasting — Model Training Pipeline [/bold cyan]")
    console.print("[bold blue]================================================================[/bold blue]\n")

    trainer = ModelTrainer(registry_dir="models", reports_dir="docs")
    comp_df, champion = trainer.run_training_pipeline(data_path="data/processed/cleaned_sales_data.csv")

    # Display Rich Comparison Table
    table = Table(title="Model Performance Comparison (Holdout Test Split)", header_style="bold magenta")
    table.add_column("Rank", justify="center", style="cyan")
    table.add_column("Model Name", style="bold")
    table.add_column("MAE (Units)", justify="right")
    table.add_column("RMSE (Units)", justify="right")
    table.add_column("WAPE (%)", justify="right")
    table.add_column("sMAPE (%)", justify="right")

    for idx, row in comp_df.iterrows():
        is_champ = (idx == 0)
        prefix = "[bold green][CHAMPION] " if is_champ else ""
        suffix = "[/bold green]" if is_champ else ""
        table.add_row(
            f"#{idx + 1}",
            f"{prefix}{row['Model']}{suffix}",
            f"{row['MAE']:.3f}",
            f"{row['RMSE']:.3f}",
            f"{row['WAPE_pct']:.2f}%",
            f"{row['sMAPE_pct']:.2f}%",
        )

    console.print("\n")
    console.print(table)
    console.print("\n[bold green][OK] Training and evaluation complete! Artifacts serialized to 'models/' and 'docs/'[/bold green]\n")


if __name__ == "__main__":
    main()
