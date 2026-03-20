from functools import lru_cache

from pydantic import Field, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Centralized configuration loaded from environment variables and .env files."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="Wafer Project API", alias="WAFER_PROJECT_APP_NAME")
    environment: str = Field(default="dev", alias="WAFER_PROJECT_ENV")
    api_key: str = Field(alias="WAFER_PROJECT_API_KEY")

    model_path: str = Field(default="models/best_model.pkl", alias="WAFER_PROJECT_MODEL_PATH")
    scaler_path: str = Field(
        default="data/Artifacts/feature_scaler.pkl",
        alias="WAFER_PROJECT_SCALER_PATH",
    )
    selected_features_path: str = Field(
        default="data/Train_data/selected_features_secom_data.csv",
        alias="WAFER_PROJECT_SELECTED_FEATURES_PATH",
    )

    request_limit_bytes: int = Field(default=1_000_000, alias="WAFER_PROJECT_REQUEST_LIMIT_BYTES")
    batch_limit_bytes: int = Field(default=10_000_000, alias="WAFER_PROJECT_BATCH_LIMIT_BYTES")

    aws_region: str = Field(default="us-east-1", alias="WAFER_PROJECT_AWS_REGION")
    s3_batch_bucket: str = Field(alias="WAFER_PROJECT_S3_BATCH_BUCKET")
    s3_dvc_uri: str = Field(default="s3://wafer-project-pm29/dvc-registry/", alias="WAFER_PROJECT_S3_DVC_URI")
    s3_mlflow_artifacts_uri: str = Field(
        default="s3://wafer-project-pm29/mlflow-artifacts/",
        alias="WAFER_PROJECT_S3_MLFLOW_ARTIFACTS_URI",
    )

    db_host: str = Field(alias="WAFER_PROJECT_DB_HOST")
    db_port: int = Field(default=5432, alias="WAFER_PROJECT_DB_PORT")
    db_name: str = Field(alias="WAFER_PROJECT_DB_NAME")
    db_user: str = Field(alias="WAFER_PROJECT_DB_USER")
    db_password: str = Field(alias="WAFER_PROJECT_DB_PASSWORD")
    db_sslmode: str = Field(default="require", alias="WAFER_PROJECT_DB_SSLMODE")

    mlflow_tracking_uri: str = Field(alias="WAFER_PROJECT_MLFLOW_TRACKING_URI")
    mlflow_experiment_name: str = Field(default="wafer-project", alias="WAFER_PROJECT_MLFLOW_EXPERIMENT_NAME")
    run_owner: str = Field(alias="WAFER_PROJECT_RUN_OWNER")
    dvc_version_id: str = Field(alias="WAFER_PROJECT_DVC_VERSION_ID")
    production_pr_auc_baseline: float = Field(default=0.0, alias="WAFER_PROJECT_PR_AUC_BASELINE")

    @property
    def sqlalchemy_db_uri(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:"
            f"{self.db_port}/{self.db_name}?sslmode={self.db_sslmode}"
        )

    @model_validator(mode="after")
    def validate_wafers(self) -> "AppSettings":
        if self.request_limit_bytes > self.batch_limit_bytes:
            raise ValueError("Request limit cannot exceed batch limit.")
        return self


def validate_required_settings() -> AppSettings:
    """Fail fast when required settings are missing or invalid."""
    try:
        return get_settings()
    except ValidationError as exc:
        raise RuntimeError(f"Missing or invalid environment configuration: {exc}") from exc


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
