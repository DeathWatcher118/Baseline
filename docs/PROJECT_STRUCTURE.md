# Project Structure Guide

This document defines the complete directory structure for the Anomaly Detection System following the established standards.

## Complete Directory Tree

```
d:/Hackathon/
├── .env.example                    # Environment variables template
├── .env                           # Environment variables (gitignored)
├── .gitignore                     # Git ignore rules
├── README.md                      # Project overview
├── STANDARDS.md                   # Development standards
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup
├── pyproject.toml                # Python project configuration
│
├── src/                          # Source code
│   ├── __init__.py
│   ├── main.py                   # Application entry point
│   │
│   ├── agent/                    # ADK Agent implementation
│   │   ├── __init__.py
│   │   ├── agent.py              # Main agent orchestration
│   │   ├── tools.py              # Agent tools/functions
│   │   ├── prompts.py            # Agent prompts
│   │   └── memory.py             # Conversation memory
│   │
│   ├── api/                      # REST API
│   │   ├── __init__.py
│   │   ├── app.py                # FastAPI application
│   │   ├── routes/               # API routes
│   │   │   ├── __init__.py
│   │   │   ├── anomalies.py
│   │   │   ├── correlations.py
│   │   │   └── reports.py
│   │   ├── models/               # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   └── middleware/           # API middleware
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── logging.py
│   │
│   ├── detection/                # Anomaly detection
│   │   ├── __init__.py
│   │   ├── detector.py           # Main detector
│   │   ├── statistical.py       # Statistical methods
│   │   ├── ml_models.py          # ML-based detection
│   │   └── thresholds.py         # Threshold configuration
│   │
│   ├── correlation/              # Correlation analysis
│   │   ├── __init__.py
│   │   ├── engine.py             # Correlation engine
│   │   ├── temporal.py           # Temporal correlation
│   │   ├── statistical.py       # Statistical correlation
│   │   └── pattern.py            # Pattern matching
│   │
│   ├── data/                     # Data processing
│   │   ├── __init__.py
│   │   ├── ingestion/            # Data ingestion
│   │   │   ├── __init__.py
│   │   │   ├── finops.py
│   │   │   ├── workload.py
│   │   │   └── migration.py
│   │   ├── processing/           # Data processing
│   │   │   ├── __init__.py
│   │   │   ├── cleaner.py
│   │   │   ├── normalizer.py
│   │   │   └── aggregator.py
│   │   └── storage/              # Data storage
│   │       ├── __init__.py
│   │       ├── bigquery.py
│   │       └── gcs.py
│   │
│   ├── models/                   # ML models
│   │   ├── __init__.py
│   │   ├── isolation_forest.py
│   │   ├── lstm_autoencoder.py
│   │   ├── prophet_model.py
│   │   └── model_registry.py
│   │
│   ├── explanation/              # AI explanations
│   │   ├── __init__.py
│   │   ├── generator.py          # Explanation generator
│   │   ├── templates.py          # Explanation templates
│   │   └── recommendations.py    # Recommendation engine
│   │
│   ├── utils/                    # Utilities
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration management
│   │   ├── logging.py            # Logging setup
│   │   ├── metrics.py            # Metrics collection
│   │   └── helpers.py            # Helper functions
│   │
│   └── schemas/                  # Data schemas
│       ├── __init__.py
│       ├── finops.py
│       ├── workload.py
│       └── anomaly.py
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   │
│   ├── unit/                     # Unit tests
│   │   ├── __init__.py
│   │   ├── test_detection.py
│   │   ├── test_correlation.py
│   │   ├── test_data_processing.py
│   │   └── test_agent.py
│   │
│   ├── integration/              # Integration tests
│   │   ├── __init__.py
│   │   ├── test_bigquery.py
│   │   ├── test_vertex_ai.py
│   │   ├── test_api_endpoints.py
│   │   └── test_agent_workflow.py
│   │
│   └── e2e/                      # End-to-end tests
│       ├── __init__.py
│       └── test_anomaly_workflow.py
│
├── terraform/                    # Infrastructure as Code
│   ├── README.md
│   ├── TERRAFORM_SETUP.md
│   │
│   ├── environments/
│   │   ├── dev/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   ├── terraform.tfvars
│   │   │   └── backend.tf
│   │   └── prod/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       ├── outputs.tf
│   │       ├── terraform.tfvars
│   │       └── backend.tf
│   │
│   ├── modules/
│   │   ├── bigquery/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── cloud-storage/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── cloud-run/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── vertex-ai/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── monitoring/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   └── networking/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── outputs.tf
│   │
│   └── scripts/
│       ├── inventory_gcp_resources.py
│       └── setup_state_bucket.sh
│
├── docs/                         # Documentation
│   ├── architecture/
│   │   ├── system-architecture.md
│   │   ├── data-flow.md
│   │   └── deployment-diagram.md
│   │
│   ├── api/
│   │   ├── openapi.yaml
│   │   └── api-guide.md
│   │
│   ├── development/
│   │   ├── setup-guide.md
│   │   ├── testing-guide.md
│   │   └── contributing.md
│   │
│   ├── operations/
│   │   ├── runbook.md
│   │   ├── troubleshooting.md
│   │   └── monitoring-guide.md
│   │
│   └── PROJECT_STRUCTURE.md      # This file
│
├── scripts/                      # Utility scripts
│   ├── setup/
│   │   ├── setup_environment.sh
│   │   ├── install_dependencies.sh
│   │   └── configure_gcp.sh
│   │
│   ├── data/
│   │   ├── generate_sample_data.py
│   │   ├── load_finops_data.py
│   │   └── load_workload_metrics.py
│   │
│   ├── deployment/
│   │   ├── build_docker.sh
│   │   ├── deploy_cloud_run.sh
│   │   └── deploy_vertex_ai.sh
│   │
│   └── maintenance/
│       ├── cleanup_old_data.py
│       └── backup_resources.sh
│
├── config/                       # Configuration files
│   ├── logging.yaml
│   ├── monitoring.yaml
│   └── agent_config.yaml
│
├── notebooks/                    # Jupyter notebooks
│   ├── exploration/
│   │   ├── data_exploration.ipynb
│   │   └── anomaly_analysis.ipynb
│   │
│   └── experiments/
│       ├── model_experiments.ipynb
│       └── correlation_experiments.ipynb
│
├── data/                         # Local data (gitignored)
│   ├── raw/
│   ├── processed/
│   └── samples/
│
├── models/                       # Trained models (gitignored)
│   ├── isolation_forest/
│   ├── lstm_autoencoder/
│   └── prophet/
│
├── docker/                       # Docker configurations
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── docker-compose.yml
│   └── .dockerignore
│
├── .github/                      # GitHub workflows (if using)
│   └── workflows/
│       ├── ci.yml
│       ├── deploy-dev.yml
│       └── deploy-prod.yml
│
└── gcp-ai-env/                   # Python virtual environment (gitignored)
```

## Directory Descriptions

### Root Level

- **`.env.example`**: Template for environment variables
- **`.env`**: Actual environment variables (never commit)
- **`.gitignore`**: Files and directories to ignore in Git
- **`README.md`**: Project overview and quick start
- **`STANDARDS.md`**: Development standards and guidelines
- **`requirements.txt`**: Python package dependencies
- **`setup.py`**: Python package setup configuration
- **`pyproject.toml`**: Modern Python project configuration

### src/ - Source Code

Main application source code organized by functionality:

#### agent/
ADK Agent implementation for orchestrating the anomaly detection workflow.

**Key Files**:
- `agent.py`: Main agent class using Vertex AI Reasoning Engine
- `tools.py`: Tool definitions for agent (query data, analyze, correlate)
- `prompts.py`: System and user prompts for agent
- `memory.py`: Conversation history and context management

#### api/
REST API built with FastAPI for external access.

**Structure**:
- `app.py`: FastAPI application setup
- `routes/`: API endpoint definitions
- `models/`: Request/response Pydantic models
- `middleware/`: Authentication, logging, error handling

#### detection/
Anomaly detection algorithms and models.

**Components**:
- `detector.py`: Main detection orchestrator
- `statistical.py`: Z-score, IQR, moving average methods
- `ml_models.py`: ML-based detection (Isolation Forest, LSTM)
- `thresholds.py`: Configurable thresholds and sensitivity

#### correlation/
Correlation analysis between anomalies and events.

**Components**:
- `engine.py`: Main correlation engine
- `temporal.py`: Time-based correlation
- `statistical.py`: Statistical correlation (Pearson, Spearman)
- `pattern.py`: Pattern matching algorithms

#### data/
Data ingestion, processing, and storage.

**Structure**:
- `ingestion/`: Load data from various sources
- `processing/`: Clean, normalize, aggregate data
- `storage/`: BigQuery and Cloud Storage interfaces

#### models/
Machine learning model implementations.

**Models**:
- `isolation_forest.py`: Scikit-learn Isolation Forest
- `lstm_autoencoder.py`: TensorFlow/PyTorch LSTM
- `prophet_model.py`: Facebook Prophet for time-series
- `model_registry.py`: Model versioning and management

#### explanation/
AI-powered explanations using Gemini.

**Components**:
- `generator.py`: Generate natural language explanations
- `templates.py`: Explanation templates
- `recommendations.py`: Actionable recommendation engine

#### utils/
Shared utilities and helpers.

**Utilities**:
- `config.py`: Configuration management
- `logging.py`: Structured logging setup
- `metrics.py`: Custom metrics collection
- `helpers.py`: Common helper functions

### tests/ - Test Suite

Comprehensive test coverage following pytest conventions.

**Structure**:
- `unit/`: Fast, isolated unit tests
- `integration/`: Tests with external dependencies (BigQuery, Vertex AI)
- `e2e/`: End-to-end workflow tests

### terraform/ - Infrastructure

Terraform configurations for GCP infrastructure.

**Organization**:
- `environments/`: Environment-specific configurations (dev, prod)
- `modules/`: Reusable Terraform modules
- `scripts/`: Helper scripts for Terraform operations

### docs/ - Documentation

Comprehensive project documentation.

**Categories**:
- `architecture/`: System design and architecture
- `api/`: API specifications and guides
- `development/`: Developer guides
- `operations/`: Operational runbooks

### scripts/ - Utility Scripts

Helper scripts for various tasks.

**Categories**:
- `setup/`: Environment setup scripts
- `data/`: Data generation and loading
- `deployment/`: Deployment automation
- `maintenance/`: Maintenance tasks

### config/ - Configuration Files

YAML configuration files for various components.

**Files**:
- `logging.yaml`: Logging configuration
- `monitoring.yaml`: Monitoring and alerting rules
- `agent_config.yaml`: Agent behavior configuration

### notebooks/ - Jupyter Notebooks

Interactive notebooks for exploration and experimentation.

**Categories**:
- `exploration/`: Data exploration and analysis
- `experiments/`: Model and algorithm experiments

### docker/ - Docker Configuration

Docker files for containerization.

**Files**:
- `Dockerfile`: Production Docker image
- `Dockerfile.dev`: Development Docker image
- `docker-compose.yml`: Multi-container setup
- `.dockerignore`: Files to exclude from Docker build

## File Naming Conventions

### Python Files
- Use lowercase with underscores: `anomaly_detector.py`
- Test files: `test_anomaly_detector.py`
- Module init: `__init__.py`

### Configuration Files
- Use lowercase with hyphens: `agent-config.yaml`
- Environment files: `.env`, `.env.example`

### Documentation
- Use uppercase for root docs: `README.md`, `STANDARDS.md`
- Use lowercase with hyphens for nested docs: `setup-guide.md`

### Terraform Files
- Standard names: `main.tf`, `variables.tf`, `outputs.tf`
- Environment-specific: `terraform.tfvars`

## Import Structure

### Absolute Imports
```python
from src.agent.agent import AnomalyDetectionAgent
from src.detection.detector import AnomalyDetector
from src.data.storage.bigquery import BigQueryClient
```

### Relative Imports (within package)
```python
from .detector import AnomalyDetector
from ..utils.config import get_config
```

## Module Organization

### Package Structure
Each major component should be a Python package with:
- `__init__.py`: Package initialization and exports
- Main implementation files
- Supporting modules
- Tests in parallel structure

### Example: detection package
```
src/detection/
├── __init__.py          # Exports: AnomalyDetector
├── detector.py          # Main detector class
├── statistical.py       # Statistical methods
├── ml_models.py         # ML models
└── thresholds.py        # Configuration

tests/unit/
└── test_detection.py    # Tests for detection package
```

## Configuration Management

### Environment Variables
```python
# .env
GCP_PROJECT_ID=ccibt-hack25ww7-730
GCP_REGION=us-central1
ENVIRONMENT=dev
LOG_LEVEL=DEBUG
```

### Configuration Files
```yaml
# config/agent_config.yaml
agent:
  model: gemini-1.5-pro
  temperature: 0.7
  max_iterations: 10
  
detection:
  methods:
    - statistical
    - ml_based
  thresholds:
    critical: 3.0
    high: 2.5
```

## Data Organization

### Local Data Structure
```
data/
├── raw/                 # Raw, unprocessed data
│   ├── finops/
│   └── workload/
├── processed/           # Cleaned, processed data
│   ├── finops/
│   └── workload/
└── samples/            # Sample data for testing
    ├── finops_sample.json
    └── workload_sample.json
```

### GCS Data Structure
```
gs://ccibt-hack25ww7-730-data/
├── finops/
│   ├── raw/YYYY/MM/DD/
│   └── processed/YYYY/MM/DD/
├── workload-metrics/
│   ├── raw/YYYY/MM/DD/
│   └── processed/YYYY/MM/DD/
└── migration-logs/
    └── YYYY/MM/DD/
```

## Model Organization

### Local Models
```
models/
├── isolation_forest/
│   ├── model_v1.pkl
│   ├── model_v2.pkl
│   └── metadata.json
├── lstm_autoencoder/
│   ├── model_v1.h5
│   └── metadata.json
└── prophet/
    ├── model_v1.pkl
    └── metadata.json
```

### Vertex AI Model Registry
- Models stored in Vertex AI Model Registry
- Versioned and tracked
- Metadata includes training metrics, parameters

## Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/correlation-engine

# Work in src/correlation/
# Write tests in tests/unit/
# Update docs in docs/
```

### 2. Testing
```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests with coverage
pytest --cov=src tests/
```

### 3. Documentation
```bash
# Update relevant docs
# - API docs if API changed
# - Architecture docs if design changed
# - README if setup changed
```

### 4. Deployment
```bash
# Build Docker image
docker build -f docker/Dockerfile -t api:latest .

# Deploy to Cloud Run
gcloud run deploy anomaly-detection-api \
  --image gcr.io/ccibt-hack25ww7-730/api:latest \
  --region us-central1
```

## Best Practices

### Code Organization
1. Keep modules focused and single-purpose
2. Use clear, descriptive names
3. Maintain consistent structure across packages
4. Document public APIs

### File Size
- Keep files under 500 lines
- Split large files into logical modules
- Use helper modules for utilities

### Dependencies
- Group related imports
- Use absolute imports for clarity
- Avoid circular dependencies

### Testing
- Mirror source structure in tests
- One test file per source file
- Group related tests in classes

## Next Steps

To implement this structure:

1. **Switch to Code Mode**: Use code mode to create the actual directory structure and files
2. **Create Core Modules**: Start with utils, data, and detection
3. **Implement Agent**: Build ADK agent with tools
4. **Build API**: Create FastAPI endpoints
5. **Add Tests**: Write comprehensive tests
6. **Deploy**: Use Terraform to deploy infrastructure

---

**Document Version**: 1.0  
**Last Updated**: 2024-12-16  
**Maintained By**: Hackathon Team