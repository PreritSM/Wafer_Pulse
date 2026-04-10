# CHecklist

Comparison basis: current branch `main` vs `fast_dev` (user requested `fast-dev`).

## Tasks Done (Implemented on `main`)

- [x] End-to-end classical ML pipeline scripts exist in `src/`:
  - `pipeline_02_data_preparation.py`
  - `pipeline_03_data_preprocessing.py`
  - `pipeline_04_feature_normalize_std.py`
  - `pipeline_05_feature_selection.py`
  - `pipeline_06_model_training.py`
  - `pipeline_07_model_inference.py`
- [x] DVC stages are defined in `dvc.yaml` for data prep, preprocessing, scaling, feature selection, training, and inference.
- [x] Model training pipeline includes RF + XGBoost GridSearch workflow and model/result serialization (`best_model.pkl`, per-model PKLs, params, training results).
- [x] Data artifacts/report generation is implemented:
  - data load report
  - missing value report
  - feature selection report
  - model training report
- [x] Feature scaler persistence (`feature_scaler.pkl`) is implemented.
- [x] Inference output persistence to `data/Prediction_Output_File/Predictions.csv` is implemented.
- [x] Basic project automation exists in `Makefile` (`requirements`, `clean`, `lint`, `format`, `test`, `help`).
- [x] Core project config and schema files are present under `config/`.

## Tasks Need To Be Completed

### A) Pending from `fast_dev` branch (not yet in `main`)

- [x] Add API layer files:
  - `src/api/main.py`
  - `src/api/schemas.py`
  - `src/api/__init__.py`
- [ ] Add infrastructure integration modules:
  - `src/infrastructure/aws_clients.py`
  - `src/infrastructure/db.py`
  - `src/infrastructure/mlflow_tracking.py`
  - `src/infrastructure/model_runtime.py`
  - `src/infrastructure/retry.py`
  - `src/infrastructure/settings.py`
  - `src/infrastructure/__init__.py`
- [ ] Add serverless ingestion handler:
  - `src/lambda_handlers/batch_ingestion.py`
  - `src/lambda_handlers/__init__.py`
- [ ] Add CI/CD workflows:
  - `.github/workflows/ci.yml`
  - `.github/workflows/daily-training.yml`
- [ ] Add containerization files:
  - `Dockerfile`
  - `.dockerignore`
- [ ] Add env template:
  - `.env.example`
- [ ] Add cloud contract file:
  - `config/cloud_provisioning_contract.yaml`
- [ ] Add full Terraform IaC files:
  - `infrastructure/terraform/main.tf`
  - `infrastructure/terraform/variables.tf`
  - `infrastructure/terraform/outputs.tf`
  - `infrastructure/terraform/.terraform.lock.hcl`
  - `infrastructure/terraform/minimal.auto.tfvars.example`
- [ ] Bring `README.md`, `requirements.txt`, `pyproject.toml`, and `pipeline_06_model_training.py` updates from `fast_dev` into `main`.
- [ ] Add missing test file from `fast_dev`: `tests/test_api_schemas.py`.

### B) Gaps visible in current `main` code quality/completion

- [ ] Replace placeholder failing unit test in `tests/test_data.py` (`assertTrue(False)`) with real tests.
- [ ] Add runnable tests for each pipeline stage and inference path.
- [ ] Wire inference for real input batch/schema validation (current flow is mostly dummy-data oriented).
- [ ] Add robust error handling + logging consistency across all pipeline scripts.
- [ ] Add/verify model registry or experiment tracking integration (MLflow lines are commented in training code).
- [ ] Ensure Terraform local/provider artifacts are not committed from local workspace state (keep only intentional IaC files tracked).

## Quick Branch Delta Summary

- `main...fast_dev` commit delta: `0 2` (main is behind by 2 commits).
- Net comparison shows `fast_dev` introduces platformization work (API + AWS infra + CI + Docker + extra tests) while `main` holds the core ML pipeline implementation.
