"""
Data Ingestion Module
=====================
Loads raw CSV sales records, inspects headers, and executes validation checks.
"""

import os
import logging
from typing import Optional, Union, Tuple
import pandas as pd

from ml.preprocessing.validator import DataValidator, ValidationReport

logger = logging.getLogger(__name__)


class DataIngestion:
    """Handles loading, file validation, and format normalization."""

    def __init__(self, validator: Optional[DataValidator] = None):
        self.validator = validator or DataValidator()

    def ingest_csv(
        self,
        file_path: str,
        validate: bool = True,
    ) -> Tuple[pd.DataFrame, Optional[ValidationReport]]:
        """
        Reads a raw CSV file into a pandas DataFrame and executes validation.

        Args:
            file_path: Path to the raw CSV file.
            validate: Whether to run schema and integrity validation.

        Returns:
            Tuple of (DataFrame, ValidationReport).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found at: {file_path}")

        logger.info(f"Ingesting sales dataset from: {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df):,} rows with {len(df.columns)} columns.")

        report = None
        if validate:
            report = self.validator.validate(df)
            if not report.is_valid:
                logger.error(f"Data validation failed for {file_path}:\n{report.summary()}")
            else:
                logger.info("Data validation passed successfully.")

        return df, report
