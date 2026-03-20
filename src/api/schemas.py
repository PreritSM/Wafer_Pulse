from pydantic import BaseModel, Field, field_validator


class PredictRequest(BaseModel):
    sensors: list[float] = Field(..., min_length=591, max_length=591)

    @field_validator("sensors")
    @classmethod
    def validate_no_nan(cls, value: list[float]) -> list[float]:
        for sensor in value:
            if sensor != sensor:
                raise ValueError("NaN values are not allowed in sensor payload")
        return value


class PredictResponse(BaseModel):
    label: str
    confidence: float
