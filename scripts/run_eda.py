"""
Run Exploratory Data Analysis & Generate Visual Assets
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pprint
import pandas as pd
from ml.preprocessing.eda import RetailEDA

if __name__ == "__main__":
    df = pd.read_csv("data/processed/cleaned_sales_data.csv")
    eda = RetailEDA(output_dir="docs/eda_reports")
    metrics = eda.run_full_eda(df)
    print("\n--- EDA METRICS SUMMARY ---")
    print("\n[Overall Sales Statistics]")
    pprint.pprint(metrics["overall"])
    print("\n[Business Factors & Lift]")
    pprint.pprint(metrics["business_factors"])
    print("\n[Inventory & Stockout Metrics]")
    pprint.pprint(metrics["inventory"])
