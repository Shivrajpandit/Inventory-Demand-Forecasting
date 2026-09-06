"""
Sales CSV Upload & Ingestion Endpoint
=====================================
"""

import os
import io
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from ml.preprocessing.validator import DataValidator
from ml.preprocessing.cleaner import DataCleaner

router = APIRouter(prefix="/data", tags=["Data Upload"])


@router.post("/upload")
async def upload_sales_csv(file: UploadFile = File(...)):
    """
    Ingests and validates uploaded retail sales CSV.
    Returns validation status, detected rows, date range, or missing column errors.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only CSV files are supported.",
        )

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV file: {str(e)}",
        )

    validator = DataValidator()
    report = validator.validate(df)

    if not report.is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Dataset validation failed.",
                "errors": report.errors,
                "missing_columns": report.missing_required_columns,
            },
        )

    # Clean dataset
    cleaner = DataCleaner()
    cleaned_df = cleaner.clean(df)

    return {
        "status": "SUCCESS",
        "message": f"Successfully ingested and validated {len(cleaned_df):,} daily sales records.",
        "filename": file.filename,
        "total_rows": len(cleaned_df),
        "unique_stores": report.unique_stores_count,
        "unique_products": report.unique_products_count,
        "date_range": report.date_range,
        "warnings": report.warnings,
    }
