from dataclasses import dataclass
import os
import subprocess
from typing import Any

import mlflow

from src.infrastructure.settings import get_settings


@dataclass
class RunContext:
    git_sha: str
    dvc_version_id: str
    run_owner: str


def _safe_cmd(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True).strip()
    except Exception:
        return "unknown"


def get_run_context() -> RunContext:
    settings = get_settings()
    git_sha = _safe_cmd(["git", "rev-parse", "HEAD"])
    run_owner = settings.run_owner or os.getenv("USER", "unknown")
    return RunContext(git_sha=git_sha, dvc_version_id=settings.dvc_version_id, run_owner=run_owner)


def configure_mlflow() -> None:
    settings = get_settings()
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)


def log_run_metadata(best_model_name: str, best_params: dict[str, Any], metrics: dict[str, float]) -> None:
    context = get_run_context()
    mlflow.set_tag("git_sha", context.git_sha)
    mlflow.set_tag("dvc_version_id", context.dvc_version_id)
    mlflow.set_tag("run_owner", context.run_owner)
    mlflow.set_tag("best_model", best_model_name)

    for key, value in best_params.items():
        mlflow.log_param(key, value)

    for key, value in metrics.items():
        mlflow.log_metric(key, value)
