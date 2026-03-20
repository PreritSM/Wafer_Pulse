# 🔬 Wafer Pulse — Predictive Maintenance for Semiconductor Manufacturing

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

> **Sensor-driven AI to preemptively identify defective silicon wafers and streamline semiconductor manufacturing quality control.**

Wafer Pulse tackles one of the most expensive problems in semiconductor fabrication — **undetected wafer defects**. By analyzing readings from **590 in-line sensors**, the system classifies wafers as **Good (−1)** or **Bad (+1)** *before* they reach downstream processing, reducing scrap costs and improving yield.

Built on the **SECOM (Semiconductor Manufacturing) dataset** (1,567 samples, 590 sensor features, ~6.6% defect rate), the pipeline handles real-world challenges: **high dimensionality, extreme class imbalance, and pervasive missing data**.

---

## ✨ Key Features

- **End-to-end ML pipeline** — from raw batch sensor files to production-ready predictions.
- **Automated data ingestion** — consolidates 30+ timestamped CSV batch files into a unified dataset.
- **Robust preprocessing** — handles 41,951+ missing values across 538 columns via imputation; removes constant/near-zero-variance features (590 → 562).
- **Feature scaling** — `StandardScaler` normalization with a persisted scaler artifact for inference parity.
- **Mutual Information feature selection** — reduces dimensionality from 562 to the **top 60 most informative sensors**.
- **Hyperparameter-tuned models** — `GridSearchCV` over Random Forest and XGBoost; best model (XGBoost) serialized for serving.
- **Batch prediction** — ingests new batch files, applies the saved scaler and feature selector, and outputs predictions.
- **Detailed artifact logging** — every pipeline stage produces human-readable reports (data profile, missing-value analysis, feature rankings, model metrics).
- **DVC-initialized** — data version control scaffolding in place for large-file tracking.
- **Code quality tooling** — `ruff` for linting and formatting with import sorting.

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|:---------|:-----------|:--------|
| **Language** | Python 3.12 | Core language |
| **Data Processing** | Pandas, NumPy | Data manipulation & numerical computing |
| **Machine Learning** | Scikit-learn | Preprocessing, feature selection, Random Forest, metrics |
| **Gradient Boosting** | XGBoost | Primary classification model |
| **Web Framework** | FastAPI | REST API for serving predictions |
| **ASGI Server** | Uvicorn | Production-grade API process in container |
| **CLI** | Click | Command-line interface |
| **Config Management** | python-dotenv | Environment variable handling |
| **Cloud** | AWS (S3, EC2, ALB, RDS, Lambda, SNS, CloudWatch, Secrets Manager) | Production deployment and operations |
| **Experiment Tracking** | MLflow | Model versioning, metadata and metric logging |
| **Data Versioning** | DVC | Large file tracking & pipeline reproducibility |
| **Build System** | Setuptools | Python package building |
| **Linting & Formatting** | Ruff | Fast Python linter + formatter |
| **Testing** | Pytest, pytest-cov | Unit testing & coverage |
| **Package Management** | uv, pip | Dependency resolution & installation |

---

## 📁 Project Structure

```
Wafer_Predictor/
│
├── Makefile                        # Build automation (install, lint, format, test, clean)
├── pyproject.toml                  # Package metadata, build config & ruff settings
├── requirements.txt                # Pinned Python dependencies
├── LICENSE                         # MIT License
├── README.md                       # ← You are here
│
├── wafer_pulse/                    # 🐍 Main Python package
│   └── __init__.py                 # Package initializer
│
├── data/
│   ├── Training_Batch_Files/       # 📥 Raw sensor CSVs (30+ batch files, 590 sensors each)
│   │   ├── Wafer_07012020_000000.csv
│   │   ├── wafer_07012020_041011.csv
│   │   └── ...                     # Naming: Wafer_DDMMYYYY_HHMMSS.csv
│   │
│   ├── Prediction_Batch_files/     # 📥 Unlabeled batch files for inference
│   │   ├── wafer_07012020_041011.csv
│   │   └── ...
│   │
│   ├── raw/                        # 🗃️ Consolidated raw dataset
│   │   └── combined_secom_data.csv #    1,567 rows × 591 cols (590 sensors + label)
│   │
│   ├── preprocessed_data/          # 🔧 Cleaned & transformed data
│   │   ├── preprocessed_secom_data.csv  # After imputation & variance filtering
│   │   └── scaled_secom_data.csv        # After StandardScaler normalization
│   │
│   ├── Train_data/                 # 🎯 Final training-ready data
│   │   └── selected_features_secom_data.csv  # Top 60 MI-selected features + label
│   │
│   ├── Prediction_Output_File/     # 📤 Model predictions
│   │   └── Predictions.csv
│   │
│   └── Artifacts/                  # 📊 Pipeline stage reports & serialized objects
│       ├── Data_load_info.txt           # Dataset shape, label distribution, failure rate
│       ├── Missing_value_processing.txt # Missing value audit (41,951 NaNs across 538 cols)
│       ├── feature_selection_report.txt # Top 60 features ranked by Mutual Information
│       ├── model_training_report.txt    # GridSearchCV results for RF & XGBoost
│       └── feature_scaler.pkl           # Persisted StandardScaler for inference
│
├── models/                         # 🤖 Serialized trained models
│   └── best_model.pkl              #    XGBoost (lr=0.5, depth=5, n=50)
│
├── src/                            # Source utilities
│   ├── api/                        # 🚀 FastAPI application (/predict, /health, /ready)
│   ├── infrastructure/             # ☁️ Cloud and integration modules (AWS/RDS/MLflow settings)
│   └── lambda_handlers/            # λ S3-triggered batch inference handlers
│
├── infrastructure/                 # 🏗️ Infrastructure as Code
│   └── terraform/                  #    AWS VPC, S3, ALB, EC2, RDS, CloudWatch, SNS
│
├── .github/workflows/              # 🔄 CI/CD and scheduled training workflows
│   ├── ci.yml
│   └── daily-training.yml
│
├── Dockerfile                      # 🐳 API container image (python:3.9-slim + uvicorn)
├── .env.example                    # 🔐 Environment variable template (WAFER_PROJECT_*)
├── tests/                          # 🧪 Test suite
│   └── test_data.py                #    Data validation tests
│
├── notebooks/                      # 📓 Jupyter notebooks (experimentation)
├── docs/                           # 📖 MkDocs documentation site
│   ├── mkdocs.yml
│   └── docs/
│
├── reports/                        # 📈 Analysis reports & visualizations
│   └── figures/
│
└── references/                     # 📚 Reference materials & data dictionaries
```

---

## ⚙️ Installation & Setup

### Prerequisites

- **Python 3.12+**
- **pip** or [**uv**](https://github.com/astral-sh/uv) (recommended)
- **Git**
- **Make** (optional, for shortcut commands)

### 1. Clone the Repository

```bash
git clone https://github.com/PreritSM/Wafer_Predictor.git
cd Wafer_Predictor
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Or using the Makefile (requires `virtualenvwrapper`):

```bash
make create_environment
```

### 3. Install Dependencies

```bash
make requirements
```

Or manually:

```bash
pip install -U pip
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import src; print('✅ wafer project imports correctly')"
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Populate all required `WAFER_PROJECT_*` values in `.env`.

---

## ☁️ Cloud Provisioning Contract

Before provisioning AWS resources, fill:

- `config/cloud_provisioning_contract.yaml`

This file is the single source for:

- Terraform input values (`api_ami_id`, CIDRs, alert email, etc.)
- Runtime environment values (`WAFER_PROJECT_*`)
- Post-provision outputs that must be handed back (`api_alb_dns_name`, `rds_endpoint`, subnet IDs, etc.)

After apply, update the `post_provision_outputs` section in `config/cloud_provisioning_contract.yaml` with real values.

---

## 🏗️ AWS Deployment (Terraform)

```bash
cd infrastructure/terraform
terraform init
terraform plan \
        -var='api_ami_id=ami-xxxxxxxxxxxxxxxxx' \
        -var='db_password=***' \
        -var='api_key=***' \
        -var='run_owner=owner@example.com' \
        -var='dvc_version_id=<dvc-version-id>' \
        -var='alert_email=you@example.com'
terraform apply
```

### Minimal Footprint Mode (Recommended)

Use this mode for low/no-load operation and lowest cost. It disables NAT, ALB, and optional observability extras.

Copy and edit the template first:

```bash
cp infrastructure/terraform/minimal.auto.tfvars.example infrastructure/terraform/minimal.auto.tfvars
```

```bash
cd infrastructure/terraform
terraform init
terraform apply -var-file="minimal.auto.tfvars"
```

To tear down everything provisioned by Terraform:

```bash
cd infrastructure/terraform
terraform destroy -var-file="minimal.auto.tfvars"
```

Provisioned components include:

- Custom VPC with public/private subnets and NAT
- S3 bucket (`s3://wafer-project-pm29/`) with versioning + SSE-S3
- RDS PostgreSQL (`db.t3.micro`)
- Internet-facing ALB + EC2 API target
- CloudWatch logs/dashboard and SNS alerts
- Secrets Manager secret for runtime config

---

## 🚀 Usage

### Makefile Commands

| Command | Description |
|:--------|:------------|
| `make requirements` | Install all Python dependencies |
| `make clean` | Remove compiled `.pyc` files and `__pycache__/` directories |
| `make lint` | Check code style with `ruff` (no auto-fix) |
| `make format` | Auto-format and fix code with `ruff` |
| `make test` | Run the test suite |
| `make help` | List all available Make targets |

### Start API Locally

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

- `GET /health` -> liveness
- `GET /ready` -> readiness (model + dependencies loaded)
- `POST /predict` -> single wafer inference (591 float sensors)

Example:

```bash
python - <<'PY'
import json
import requests

payload = {"sensors": [0.0] * 591}
resp = requests.post(
                "http://localhost:8000/predict",
                headers={"x-api-key": "<WAFER_PROJECT_API_KEY>"},
                json=payload,
                timeout=10,
)
print(resp.status_code)
print(json.dumps(resp.json(), indent=2))
PY
```

Note: The `sensors` array must contain exactly `591` floating-point values.

### Pipeline Overview

The ML pipeline flows through the following stages, with each stage reading from the previous stage's output:

```
Training_Batch_Files/*.csv
        │
        ▼
┌───────────────────┐     ┌──────────────────────────────┐
│  Data Ingestion   │────▶│  raw/combined_secom_data.csv  │
└───────────────────┘     └──────────────────────────────┘
        │
        ▼
┌───────────────────┐     ┌────────────────────────────────────────┐
│  Preprocessing    │────▶│  preprocessed_data/preprocessed_*.csv  │
│  (impute + filter)│     └────────────────────────────────────────┘
└───────────────────┘
        │
        ▼
┌───────────────────┐     ┌──────────────────────────────────────┐
│  Feature Scaling  │────▶│  preprocessed_data/scaled_*.csv      │
│  (StandardScaler) │     │  Artifacts/feature_scaler.pkl        │
└───────────────────┘     └──────────────────────────────────────┘
        │
        ▼
┌───────────────────┐     ┌──────────────────────────────────────┐
│  Feature Selection│────▶│  Train_data/selected_features_*.csv  │
│  (Mutual Info)    │     │  Top 60 of 562 features              │
└───────────────────┘     └──────────────────────────────────────┘
        │
        ▼
┌───────────────────┐     ┌──────────────────────────────────────┐
│  Model Training   │────▶│  models/best_model.pkl               │
│  (RF vs XGBoost)  │     │  XGBoost selected (AUC = 0.6958)    │
└───────────────────┘     └──────────────────────────────────────┘
        │
        ▼
┌───────────────────┐     ┌──────────────────────────────────────┐
│  Prediction       │────▶│  Prediction_Output_File/Predictions  │
└───────────────────┘     └──────────────────────────────────────┘
```

### Model Performance

| Model | Best Parameters | CV Score | Accuracy | Precision | F1 | ROC-AUC |
|:------|:---------------|:---------|:---------|:----------|:---|:--------|
| **Random Forest** | `gini`, `max_depth=2`, `log2`, `n=10` | 0.9338 | 0.9331 | 0.8707 | 0.9008 | 0.6079 |
| **XGBoost** ✅ | `lr=0.5`, `max_depth=5`, `n=50` | 0.9354 | 0.9172 | 0.8899 | 0.9015 | **0.6958** |

> **Note:** Model selection in the current training pipeline is PR-AUC first (as primary metric for class imbalance), with ROC-AUC and F1 logged as supporting metrics.

### Dataset Summary

| Property | Value |
|:---------|:------|
| Samples | 1,567 |
| Sensors (raw features) | 590 |
| Selected features | 60 |
| Good wafers (−1) | 1,463 (93.4%) |
| Defective wafers (+1) | 104 (6.6%) |
| Missing values | 41,951 (4.53% of all cells) |

---

## 🗺️ Implementation Status

### ✅ Completed

- FastAPI service implemented in `src/api/` with `/predict`, `/health`, `/ready`.
- API key enforcement and payload limits (`1MB` request / `10MB` batch object).
- Cloud integration layer in `src/infrastructure/` for settings, retries, S3, RDS persistence, and MLflow tagging.
- Batch ingestion Lambda handler in `src/lambda_handlers/batch_ingestion.py`.
- DVC remote switched to `s3://wafer-project-pm29/dvc-registry/`.
- Terraform scaffold in `infrastructure/terraform/` for VPC, S3, ALB, EC2, RDS, CloudWatch, SNS.
- CI workflows added in `.github/workflows/` including daily training schedule and PR-AUC gate.

### 🔜 Next Steps

- Apply Terraform with real account values and capture generated outputs in `config/cloud_provisioning_contract.yaml`.
- Configure Secrets Manager values and start API container on EC2.
- Execute smoke tests against ALB endpoint and Lambda S3 trigger.
- Enable MLflow model promotion flow (Staging/Production aliases) in your hosted MLflow server.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**PreritSM** — [GitHub](https://github.com/PreritSM)

---

