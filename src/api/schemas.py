from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class PredictRequest:
    """Single wafer prediction request — expects exactly 60 scaled sensor values."""
    sensor_readings: list[float]

    def validate(self) -> Optional[str]:
        if not isinstance(self.sensor_readings, list):
            return "sensor_readings must be a list of floats"
        if len(self.sensor_readings) != 60:
            return f"Expected 60 sensor readings, got {len(self.sensor_readings)}"
        if not all(isinstance(v, (int, float)) for v in self.sensor_readings):
            return "All sensor readings must be numeric"
        return None

    @classmethod
    def from_dict(cls, data: dict) -> "PredictRequest":
        return cls(sensor_readings=data.get("sensor_readings", []))


@dataclass
class PredictResponse:
    """Single wafer prediction response."""
    prediction: int          # -1 = Good, +1 = Defective
    label: str               # "Good" or "Defective"
    inference_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "prediction": self.prediction,
            "label": self.label,
            "inference_time": self.inference_time,
        }


@dataclass
class BatchPredictRequest:
    """Batch wafer prediction request — list of wafer sensor readings."""
    wafers: list[list[float]]

    def validate(self) -> Optional[str]:
        if not isinstance(self.wafers, list) or len(self.wafers) == 0:
            return "wafers must be a non-empty list"
        for i, row in enumerate(self.wafers):
            if not isinstance(row, list) or len(row) != 60:
                return f"wafer[{i}]: expected 60 sensor readings, got {len(row) if isinstance(row, list) else 'invalid'}"
            if not all(isinstance(v, (int, float)) for v in row):
                return f"wafer[{i}]: all sensor readings must be numeric"
        return None

    @classmethod
    def from_dict(cls, data: dict) -> "BatchPredictRequest":
        return cls(wafers=data.get("wafers", []))


@dataclass
class BatchPredictResponse:
    """Batch wafer prediction response."""
    predictions: list[dict]  # list of {"prediction": int, "label": str}
    total: int
    defective_count: int
    inference_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "predictions": self.predictions,
            "total": self.total,
            "defective_count": self.defective_count,
            "inference_time": self.inference_time,
        }


@dataclass
class HealthResponse:
    status: str
    model_loaded: bool
    model_path: str

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "model_loaded": self.model_loaded,
            "model_path": self.model_path,
        }
