from dataclasses import dataclass
import os

import joblib
import pandas as pd
from sklearn.base import BaseEstimator

from src.infrastructure.settings import get_settings


@dataclass
class PredictionResult:
    label: str
    confidence: float
    raw_prediction: int


class ModelRuntime:
    """Runtime adapter that enforces training/inference parity using saved artifacts."""

    def __init__(self) -> None:
        settings = get_settings()
        self.model: BaseEstimator = self._load_pickle(settings.model_path)
        self.scaler = self._load_pickle(settings.scaler_path)
        self.selected_features = self._load_selected_features(settings.selected_features_path)

    @staticmethod
    def _load_pickle(path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required artifact not found: {path}")
        return joblib.load(path)

    @staticmethod
    def _load_selected_features(path: str) -> list[str]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Selected features file not found: {path}")
        columns = pd.read_csv(path, nrows=1).columns.tolist()
        return [col for col in columns if col != "Output"]

    def _sensor_payload_to_frame(self, sensors: list[float]) -> pd.DataFrame:
        sensor_columns = [f"Sensor_{i}" for i in range(len(sensors))]
        row = pd.DataFrame([sensors], columns=sensor_columns)

        scaler_columns = list(getattr(self.scaler, "feature_names_in_", []))
        if not scaler_columns:
            scaler_columns = sensor_columns

        for col in scaler_columns:
            if col not in row.columns:
                row[col] = 0.0

        return row[scaler_columns]

    def predict(self, sensors: list[float]) -> PredictionResult:
        raw_frame = self._sensor_payload_to_frame(sensors)
        scaled = self.scaler.transform(raw_frame)
        scaled_df = pd.DataFrame(scaled, columns=raw_frame.columns)

        for feat in self.selected_features:
            if feat not in scaled_df.columns:
                scaled_df[feat] = 0.0

        model_input = scaled_df[self.selected_features]

        pred = int(self.model.predict(model_input)[0])
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(model_input)[0]
            confidence = float(max(probabilities))
        else:
            confidence = 1.0

        label = "Fail" if pred == 1 else "Pass"
        return PredictionResult(label=label, confidence=confidence, raw_prediction=pred)
