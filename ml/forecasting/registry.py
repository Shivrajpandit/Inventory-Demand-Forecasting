"""
Model Registry & Artifact Serializer
====================================
Manages saving, loading, versioning, and tracking metadata for trained forecasting models.
"""

import os
import json
import joblib
from datetime import datetime
from typing import Dict, Any, Optional


class ModelRegistry:
    """Handles serialization and versioning of trained model artifacts."""

    def __init__(self, registry_dir: str = "models"):
        self.registry_dir = registry_dir
        os.makedirs(self.registry_dir, exist_ok=True)

    def save_model(
        self,
        model_obj: Any,
        model_name: str,
        metrics: Dict[str, float],
        hyperparameters: Dict[str, Any],
        feature_importance: Dict[str, float],
        version: str = "1.0.0",
        is_champion: bool = False,
    ) -> str:
        """
        Saves a trained model artifact and its lineage metadata.
        """
        clean_name = model_name.lower().replace(" ", "_")
        artifact_filename = f"{clean_name}_v{version}.joblib"
        artifact_path = os.path.join(self.registry_dir, artifact_filename)

        # Save model binary
        joblib.dump(model_obj, artifact_path)

        # Save metadata record
        metadata = {
            "model_name": model_name,
            "version": version,
            "saved_at": datetime.utcnow().isoformat(),
            "artifact_file": artifact_filename,
            "artifact_path": artifact_path,
            "metrics": metrics,
            "hyperparameters": hyperparameters,
            "feature_importance": feature_importance,
            "is_champion": is_champion,
        }

        metadata_path = os.path.join(self.registry_dir, f"{clean_name}_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        if is_champion:
            # Save champion pointer
            champion_path = os.path.join(self.registry_dir, "champion_model.joblib")
            joblib.dump(model_obj, champion_path)
            champion_meta_path = os.path.join(self.registry_dir, "champion_metadata.json")
            with open(champion_meta_path, "w") as f:
                json.dump(metadata, f, indent=2)

        return artifact_path

    def load_model(self, model_filename: str) -> Any:
        """Loads a model artifact from disk."""
        path = os.path.join(self.registry_dir, model_filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model artifact not found at: {path}")
        return joblib.load(path)

    def load_champion_model(self) -> Any:
        """Loads the current active champion model."""
        path = os.path.join(self.registry_dir, "champion_model.joblib")
        if not os.path.exists(path):
            raise FileNotFoundError("Champion model not found. Train models first.")
        return joblib.load(path)

    def load_champion_metadata(self) -> Dict[str, Any]:
        """Loads metadata for the champion model."""
        path = os.path.join(self.registry_dir, "champion_metadata.json")
        if not os.path.exists(path):
            raise FileNotFoundError("Champion metadata not found.")
        with open(path, "r") as f:
            return json.load(f)
