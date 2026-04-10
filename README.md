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
| **Web Framework** | Flask | REST API for serving predictions |
| **WSGI Server** | Gunicorn | Production-grade HTTP server |
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
Wafer_Pulse/
│
├── Makefile                        # Build automation (install, lint, format, test, clean)
├── pyproject.toml                  # Package metadata, build config & ruff settings
├── requirements.txt                # Pinned Python dependencies
├── LICENSE                         # MIT License
├── README.md                       # ← You are here
├── Dockerfile                      # 🐳 API container image (python:3.12-slim + gunicorn)
├── .env.example                    # 🔐 Environment variable template (WAFER_PROJECT_*)
│
├── data/
│   ├── Training_Batch_Files/       # 📥 Raw sensor CSVs (30+ batch files, 590 sensors each)
│   ├── Prediction_Batch_files/     # 📥 Unlabeled batch files for inference
│   ├── raw/                        # 🗃️ Consolidated raw dataset
│   ├── preprocessed_data/          # 🔧 Cleaned & transformed data
│   ├── Train_data/                 # 🎯 Final training-ready data (top 60 MI features)
│   ├── Prediction_Output_File/     # 📤 Model predictions
│   └── Artifacts/                  # 📊 Pipeline reports & serialized objects (scaler, etc.)
│
├── models/                         # 🤖 Serialized trained models
│   └── best_model.pkl              #    XGBoost (lr=0.5, depth=5, n=50)
│
├── src/
│   ├── api/                        # 🚀 Flask API (/predict, /predict/batch, /health)
│   ├── infrastructure/             # ☁️ Cloud integration (AWS/RDS/MLflow/settings)
│   ├── lambda_handlers/            # λ S3-triggered batch inference handler
│   └── pipeline_0*.py              # ML pipeline stages (prep → preprocess → train → infer)
│
├── infrastructure/
│   └── terraform/                  # 🏗️ AWS IaC: VPC, S3, ALB, EC2, RDS, CloudWatch, SNS
│
├── .github/workflows/              # 🔄 CI/CD and scheduled training workflows
│   ├── ci.yml
│   └── daily-training.yml
│
├── config/
│   ├── params.yaml                 # Pipeline hyperparameters and paths
│   ├── cloud_provisioning_contract.yaml  # AWS resource contract & post-provision outputs
│   ├── schema_training.json
│   └── schema_prediction.json
│
├── tests/                          # 🧪 Test suite
├── notebooks/                      # 📓 Jupyter notebooks (experimentation)
├── docs/                           # 📖 MkDocs documentation site
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
git clone https://github.com/PreritSM/Wafer_Pulse.git
cd Wafer_Pulse
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

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

After apply, update the `post_provision_outputs` section with real values.

---

## 🏗️ AWS Deployment (Terraform)

```bash
cd infrastructure/terraform

# Copy the example config and fill in real values
cp minimal.auto.tfvars.example minimal.auto.tfvars
# Edit minimal.auto.tfvars — set api_ami_id, db_password, api_key, alert_email

# Download providers (~674 MB, kept out of git)
terraform init

# Preview
terraform plan -var-file="minimal.auto.tfvars"

# Apply
terraform apply -var-file="minimal.auto.tfvars"

# Tear down
terraform destroy -var-file="minimal.auto.tfvars"
```

Provisioned components include:

- Custom VPC with public/private subnets
- S3 bucket (`s3://wafer-project-pm29/`) with versioning + SSE-S3
- RDS PostgreSQL (`db.t3.micro`)
- Optional internet-facing ALB + EC2 API target
- CloudWatch logs and optional SNS alerts
- Secrets Manager secret for runtime config

> **Note:** `minimal.auto.tfvars` is gitignored. Only `minimal.auto.tfvars.example` (with placeholders) is committed. Never commit a tfvars file with real credentials.

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
python src/api/main.py
# or with gunicorn:
gunicorn --chdir src "api.main:app" --bind 0.0.0.0:5000
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Liveness — model load status |
| `POST` | `/predict` | Single wafer inference (60 scaled sensor readings) |
| `POST` | `/predict/batch` | Batch inference — list of wafers |

Example:

```bash
curl -s -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"sensor_readings": [0.0, 0.1, ...]}' | python -m json.tool
```

> The `sensor_readings` array must contain exactly **60** pre-scaled floating-point values (output of `StandardScaler` + Mutual Information feature selection).

### Pipeline Overview

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
│  (RF vs XGBoost)  │     │  Logged to MLflow                    │
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

> **Note:** Model selection uses PR-AUC as the primary metric (best for class imbalance at 6.6% defect rate). ROC-AUC and F1 are logged as supporting metrics.

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

- Flask API in `src/api/` with `/predict`, `/predict/batch`, `/health`.
- Cloud integration layer in `src/infrastructure/` for settings, retries, S3, RDS persistence, and MLflow tagging.
- Batch ingestion Lambda handler in `src/lambda_handlers/batch_ingestion.py`.
- DVC remote configured to `s3://wafer-project-pm29/dvc-registry/`.
- Terraform scaffold in `infrastructure/terraform/` for VPC, S3, ALB, EC2, RDS, CloudWatch, SNS.
- CI workflows in `.github/workflows/` including daily training schedule and PR-AUC gate.
- MLflow tracking wired into `pipeline_06_model_training.py`.

### 🔜 Next Steps

- Apply Terraform with real account values and capture outputs in `config/cloud_provisioning_contract.yaml`.
- Configure Secrets Manager and start API container on EC2.
- Execute smoke tests against the ALB endpoint and Lambda S3 trigger.
- Enable MLflow model promotion flow (Staging/Production aliases).

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**PreritSM** — [GitHub](https://github.com/PreritSM)
