# Development Setup Guide

Complete guide for setting up the Anomaly Detection System development environment.

## Prerequisites

### Required Software

1. **Python 3.14+**
   - Already installed at: `C:\Users\Brian Onstot\AppData\Local\Programs\Python\Python314`
   - Virtual environment: `gcp-ai-env` (already created)

2. **Google Cloud SDK**
   - Version: 549.0.1
   - Location: `C:\Users\Brian Onstot\AppData\Local\Google\Cloud SDK\google-cloud-sdk`

3. **Git**
   - For version control

4. **Terraform** (>= 1.5.0)
   - For infrastructure management
   - Install: `choco install terraform`

5. **Docker** (Optional)
   - For containerization
   - Install: Docker Desktop for Windows

6. **VS Code** (Recommended)
   - With Python extension
   - With Terraform extension

### GCP Account Setup

- **Account**: devstar7302@gcplab.me
- **Project ID**: ccibt-hack25ww7-730
- **Region**: us-central1
- **Zone**: us-central1-a

---

## Step 1: Clone Repository

```bash
# Navigate to your workspace
cd d:/Hackathon

# If starting fresh, initialize git
git init
git remote add origin <your-repo-url>
```

---

## Step 2: Python Environment Setup

### Activate Virtual Environment

```powershell
# Activate the existing virtual environment
.\gcp-ai-env\Scripts\Activate.ps1

# Verify Python version
python --version
# Should show: Python 3.14.0
```

### Install Dependencies

```bash
# Install core dependencies
pip install --upgrade pip

# Install from requirements.txt (to be created)
pip install -r requirements.txt

# Or install packages individually
pip install \
  google-cloud-aiplatform \
  google-cloud-bigquery \
  google-cloud-storage \
  google-cloud-monitoring \
  google-cloud-logging \
  google-generativeai \
  fastapi \
  uvicorn \
  pydantic \
  pandas \
  numpy \
  scikit-learn \
  tensorflow \
  torch \
  prophet \
  python-dotenv \
  pytest \
  pytest-cov \
  black \
  ruff
```

### Create requirements.txt

```text
# GCP Services
google-cloud-aiplatform>=1.38.0
google-cloud-bigquery>=3.13.0
google-cloud-storage>=2.10.0
google-cloud-monitoring>=2.16.0
google-cloud-logging>=3.8.0
google-cloud-secret-manager>=2.16.4
google-generativeai>=0.3.0

# API Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
python-multipart>=0.0.6

# Data Processing
pandas>=2.1.0
numpy>=1.26.0
pyarrow>=14.0.0

# ML/AI
scikit-learn>=1.3.0
tensorflow>=2.15.0
torch>=2.1.0
prophet>=1.1.5
transformers>=4.35.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0.1
requests>=2.31.0
httpx>=0.25.0

# Development
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
black>=23.11.0
ruff>=0.1.0
mypy>=1.7.0

# Monitoring
opentelemetry-api>=1.21.0
opentelemetry-sdk>=1.21.0
opentelemetry-instrumentation-fastapi>=0.42b0
```

---

## Step 3: GCP Authentication

### Application Default Credentials

```bash
# Authenticate with GCP
gcloud auth application-default login

# Set project
gcloud config set project ccibt-hack25ww7-730

# Verify authentication
gcloud auth list

# Verify project
gcloud config get-value project
```

### Service Account (Optional)

For production or CI/CD:

```bash
# Create service account
gcloud iam service-accounts create anomaly-detection-sa \
  --display-name="Anomaly Detection Service Account" \
  --project=ccibt-hack25ww7-730

# Grant necessary roles
gcloud projects add-iam-policy-binding ccibt-hack25ww7-730 \
  --member="serviceAccount:anomaly-detection-sa@ccibt-hack25ww7-730.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding ccibt-hack25ww7-730 \
  --member="serviceAccount:anomaly-detection-sa@ccibt-hack25ww7-730.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding ccibt-hack25ww7-730 \
  --member="serviceAccount:anomaly-detection-sa@ccibt-hack25ww7-730.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=anomaly-detection-sa@ccibt-hack25ww7-730.iam.gserviceaccount.com
```

---

## Step 4: Environment Configuration

### Create .env File

```bash
# Copy example to .env
cp .env.example .env
```

### Edit .env File

```bash
# GCP Configuration
GCP_PROJECT_ID=ccibt-hack25ww7-730
GCP_REGION=us-central1
GCP_ZONE=us-central1-a

# Environment
ENVIRONMENT=dev
LOG_LEVEL=DEBUG

# Google Cloud Authentication (if using service account)
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# Gemini API (if using directly)
GEMINI_API_KEY=your-gemini-api-key-here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# BigQuery
BIGQUERY_DATASET_FINOPS=finops_data
BIGQUERY_DATASET_WORKLOAD=workload_metrics
BIGQUERY_DATASET_ANOMALY=anomaly_results
BIGQUERY_DATASET_CORRELATION=correlations

# Cloud Storage
GCS_BUCKET_DATA=ccibt-hack25ww7-730-dev-data
GCS_BUCKET_MODELS=ccibt-hack25ww7-730-dev-models

# Anomaly Detection
ANOMALY_THRESHOLD_CRITICAL=3.0
ANOMALY_THRESHOLD_HIGH=2.5
ANOMALY_THRESHOLD_MEDIUM=2.0
ANOMALY_THRESHOLD_LOW=1.5
MIN_CONFIDENCE=0.75

# Agent Configuration
AGENT_MODEL=gemini-1.5-pro
AGENT_TEMPERATURE=0.7
AGENT_MAX_ITERATIONS=10

# Monitoring
ENABLE_MONITORING=true
ENABLE_TRACING=true
```

---

## Step 5: Enable GCP APIs

```bash
# Enable all required APIs
gcloud services enable \
  compute.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudfunctions.googleapis.com \
  pubsub.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com \
  secretmanager.googleapis.com \
  --project=ccibt-hack25ww7-730

# Verify enabled APIs
gcloud services list --enabled --project=ccibt-hack25ww7-730
```

---

## Step 6: Terraform Setup

### Initialize Terraform State Bucket

```bash
# Navigate to terraform directory
cd terraform

# Run setup script
.\scripts\setup_state_bucket.sh

# Or manually create bucket
gcloud storage buckets create gs://ccibt-hack25ww7-730-terraform-state \
  --project=ccibt-hack25ww7-730 \
  --location=us-central1 \
  --uniform-bucket-level-access

# Enable versioning
gcloud storage buckets update gs://ccibt-hack25ww7-730-terraform-state \
  --versioning
```

### Initialize Terraform

```bash
# Navigate to dev environment
cd terraform/environments/dev

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive

# Plan infrastructure
terraform plan -out=tfplan

# Review plan
terraform show tfplan
```

---

## Step 7: Create Project Structure

```bash
# Navigate to project root
cd d:/Hackathon

# Create directory structure
mkdir -p src/{agent,api,detection,correlation,data,models,explanation,utils,schemas}
mkdir -p src/api/{routes,models,middleware}
mkdir -p src/data/{ingestion,processing,storage}
mkdir -p tests/{unit,integration,e2e}
mkdir -p docs/{architecture,api,development,operations}
mkdir -p scripts/{setup,data,deployment,maintenance}
mkdir -p config
mkdir -p notebooks/{exploration,experiments}
mkdir -p docker

# Create __init__.py files
New-Item -ItemType File -Path src/__init__.py
New-Item -ItemType File -Path src/agent/__init__.py
New-Item -ItemType File -Path src/api/__init__.py
# ... (create for all packages)
```

---

## Step 8: Verify Setup

### Test GCP Connection

```bash
# Run existing test script
python test_gcp_connection.py

# Should output:
# [OK] Project ID: ccibt-hack25ww7-730
# [OK] BigQuery client initialized successfully
# SUCCESS: GCP Connection Test Passed
```

### Test Python Environment

```python
# Create test_setup.py
import sys
import google.cloud.bigquery
import google.cloud.aiplatform
import fastapi
import pandas as pd
import numpy as np

print("Python version:", sys.version)
print("BigQuery:", google.cloud.bigquery.__version__)
print("Vertex AI:", google.cloud.aiplatform.__version__)
print("FastAPI:", fastapi.__version__)
print("Pandas:", pd.__version__)
print("NumPy:", np.__version__)
print("\nAll imports successful!")
```

```bash
# Run test
python test_setup.py
```

### Test Terraform

```bash
cd terraform/environments/dev
terraform plan
# Should show planned infrastructure changes
```

---

## Step 9: IDE Configuration

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/gcp-ai-env/Scripts/python.exe",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true,
    ".mypy_cache": true,
    "gcp-ai-env": true
  },
  "[python]": {
    "editor.rulers": [100],
    "editor.tabSize": 4
  },
  "[terraform]": {
    "editor.defaultFormatter": "hashicorp.terraform",
    "editor.formatOnSave": true
  }
}
```

### VS Code Extensions

Install these extensions:
- Python (Microsoft)
- Pylance (Microsoft)
- Terraform (HashiCorp)
- YAML (Red Hat)
- Docker (Microsoft)
- GitLens (GitKraken)

---

## Step 10: Development Workflow

### Daily Workflow

```bash
# 1. Activate environment
.\gcp-ai-env\Scripts\Activate.ps1

# 2. Pull latest changes
git pull origin main

# 3. Create feature branch
git checkout -b feature/your-feature-name

# 4. Make changes and test
python -m pytest tests/

# 5. Format code
black src/ tests/
ruff check src/ tests/

# 6. Commit changes
git add .
git commit -m "feat: your feature description"

# 7. Push changes
git push origin feature/your-feature-name
```

### Running the API Locally

```bash
# Start API server
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Access API docs
# http://localhost:8000/docs
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_detection.py

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

---

## Step 11: Sample Data Setup

### Generate Sample Data

```bash
# Run data generation script
python scripts/data/generate_sample_data.py

# Load sample data to BigQuery
python scripts/data/load_finops_data.py
python scripts/data/load_workload_metrics.py
```

---

## Troubleshooting

### Common Issues

#### 1. Python Import Errors

```bash
# Ensure virtual environment is activated
.\gcp-ai-env\Scripts\Activate.ps1

# Reinstall packages
pip install -r requirements.txt --force-reinstall
```

#### 2. GCP Authentication Errors

```bash
# Re-authenticate
gcloud auth application-default login

# Check credentials
gcloud auth list

# Verify project
gcloud config get-value project
```

#### 3. Terraform State Lock

```bash
# If state is locked
cd terraform/environments/dev
terraform force-unlock <LOCK_ID>
```

#### 4. Port Already in Use

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

#### 5. Module Not Found

```bash
# Add project root to PYTHONPATH
$env:PYTHONPATH = "d:\Hackathon"

# Or in .env
PYTHONPATH=d:\Hackathon
```

---

## Next Steps

After completing setup:

1. **Review Documentation**
   - Read [`STANDARDS.md`](../../STANDARDS.md)
   - Review [`system-architecture.md`](../architecture/system-architecture.md)
   - Study [`API_SPECIFICATION.md`](../api/API_SPECIFICATION.md)

2. **Deploy Infrastructure**
   ```bash
   cd terraform/environments/dev
   terraform apply
   ```

3. **Start Development**
   - Implement core modules
   - Write tests
   - Build API endpoints
   - Deploy ADK agent

4. **Test Integration**
   - Test with sample data
   - Verify API endpoints
   - Test agent workflows

5. **Deploy to Cloud Run**
   - Build Docker image
   - Deploy to Cloud Run
   - Test production deployment

---

## Useful Commands Reference

### Python

```bash
# Activate environment
.\gcp-ai-env\Scripts\Activate.ps1

# Deactivate environment
deactivate

# Install package
pip install <package-name>

# Update package
pip install --upgrade <package-name>

# List installed packages
pip list

# Freeze requirements
pip freeze > requirements.txt
```

### GCP

```bash
# Set project
gcloud config set project ccibt-hack25ww7-730

# List resources
gcloud compute instances list
gcloud storage buckets list
bq ls

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Deploy to Cloud Run
gcloud run deploy <service-name> --image <image-url> --region us-central1
```

### Git

```bash
# Status
git status

# Create branch
git checkout -b feature/name

# Commit
git add .
git commit -m "message"

# Push
git push origin branch-name

# Pull
git pull origin main
```

### Docker

```bash
# Build image
docker build -t anomaly-detection-api:latest .

# Run container
docker run -p 8000:8000 anomaly-detection-api:latest

# List containers
docker ps

# Stop container
docker stop <container-id>
```

---

## Support

For issues or questions:
1. Check this guide
2. Review [STANDARDS.md](../../STANDARDS.md)
3. Check [troubleshooting guide](../operations/troubleshooting.md)
4. Contact team lead

---

**Document Version**: 1.0  
**Last Updated**: 2024-12-16  
**Maintained By**: Hackathon Team