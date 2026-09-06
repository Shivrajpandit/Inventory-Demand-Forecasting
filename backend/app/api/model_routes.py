"""
Model Performance & Explainability Endpoints
============================================
"""

import os
import json
from fastapi import APIRouter, HTTPException
from backend.app.core.config import settings
from ml.forecasting.registry import ModelRegistry

router = APIRouter(prefix="/models", tags=["Model Intelligence"])


@router.get("/performance")
def get_model_performance():
    """Returns benchmark comparison table across all trained models."""
    comp_path = os.path.join("docs", "model_comparison.json")
    if os.path.exists(comp_path):
        with open(comp_path, "r") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Model comparison report not found.")


@router.get("/champion")
def get_champion_details():
    """Returns champion model lineage, hyperparameters, metrics, and feature importances."""
    registry = ModelRegistry(registry_dir=settings.MODEL_REGISTRY_PATH)
    try:
        return registry.load_champion_metadata()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Champion metadata not found: {str(e)}")
