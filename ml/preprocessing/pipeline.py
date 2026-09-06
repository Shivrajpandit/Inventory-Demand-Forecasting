"""
Preprocessing Pipeline Orchestrator
===================================
Orchestrates raw data ingestion, schema validation, cleaning, and persistence.
"""

import os
import logging
from typing import Optional, Tuple
import pandas as pd

from ml.preprocessing.validator import DataValidator, ValidationReport
from ml.preprocessing.cleaner import DataCleaner
from ml.preprocessing.ingestion import DataIngestion

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """End-to-end preprocessing pipeline for sales and demand time-series."""

    def __init__(
        self,
        validator: Optional[DataValidator] = None,
        cleaner: Optional[DataCleaner] = None,
    ):
        self.validator = validator or DataValidator()
        self.cleaner = cleaner or DataCleaner()
        self.ingestion = DataIngestion(validator=self.validator)

    def run(
        self,
        raw_csv_path: str,
        output_csv_path: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, ValidationReport]:
        """
        Executes end-to-end preprocessing workflow:
        1. Ingest raw CSV
        2. Validate schema & content
        3. Clean data & complete date grid
        4. Save processed dataset (optional)
        """
        logger.info("Starting Data Preprocessing Pipeline...")
        raw_df, report = self.ingestion.ingest_csv(raw_csv_path, validate=True)

        if not report.is_valid:
            logger.warning(f"Validation warnings/errors:\n{report.summary()}")

        cleaned_df = self.cleaner.clean(raw_df)
        logger.info(f"Cleaned dataset: {len(cleaned_df):,} daily records generated across {cleaned_df['Store_ID'].nunique()} stores and {cleaned_df['Product_ID'].nunique()} SKUs.")

        if output_csv_path:
            os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
            cleaned_df.to_csv(output_csv_path, index=False)
            logger.info(f"Saved processed dataset to: {output_csv_path}")

        return cleaned_df, report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run retail demand data preprocessing pipeline.")
    parser.add_argument("--input", type=str, default="data/raw/sales_data.csv", help="Path to input raw CSV.")
    parser.add_argument("--output", type=str, default="data/processed/cleaned_sales_data.csv", help="Path to output cleaned CSV.")
    args = parser.parse_args()

    pipeline = PreprocessingPipeline()
    if os.path.exists(args.input):
        pipeline.run(args.input, args.output)
    else:
        print(f"Input file not found: {args.input}. Generate sample data first using scripts/generate_sample_data.py")
