# Application Development Standards

## Project Overview

**Challenge**: Anomaly Detection and Correlation Agentic Solution  
**Purpose**: Explain and correlate volume spikes in operational/financial reports, reducing investigation time from hours/days to minutes  
**GCP Project**: ccibt-hack25ww7-730  
**Primary Region**: us-central1

---

## 1. Infrastructure Standards

### 1.1 Terraform as Infrastructure-as-Code (IaC)

**Principle**: All GCP infrastructure MUST be defined and managed through Terraform.

#### Directory Structure
```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── terraform.tfvars
├── modules/
│   ├── vertex-ai/
│   ├── bigquery/
│   ├── cloud-storage/
│   ├── cloud-run/
│   └── monitoring/
└── README.md
```

#### Terraform Standards
- **Version**: Use Terraform >= 1.5.0
- **State Management**: Store state in GCS bucket with versioning enabled
- **Naming Convention**: `{project}-{environment}-{resource-type}-{name}`
- **Tagging**: All resources MUST include labels:
  - `environment`: dev/staging/prod
  - `project`: hackathon-anomaly-detection
  - `managed-by`: terraform
  - `cost-center`: hackathon

#### Required Terraform Providers
```hcl
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "ccibt-hack25ww7-730-terraform-state"
    prefix = "terraform/state"
  }
}
```

### 1.2 GCP as Source of Truth

**Principle**: GCP Console and APIs are the authoritative source for existing infrastructure state.

#### Pre-Terraform Audit Process
1. **Inventory Existing Resources**
   ```bash
   # List all resources in project
   gcloud asset search-all-resources \
     --project=ccibt-hack25ww7-730 \
     --format=json > gcp-inventory.json
   ```

2. **Import Existing Resources**
   - Document all existing resources before creating Terraform
   - Use `terraform import` for resources that must be preserved
   - Create data sources for read-only references

3. **Change Management**
   - All infrastructure changes MUST go through Terraform
   - Manual changes in GCP Console are PROHIBITED in production
   - Emergency manual changes MUST be documented and back-ported to Terraform within 24 hours

#### GCP Resource Discovery Commands
```bash
# List all enabled APIs
gcloud services list --enabled --project=ccibt-hack25ww7-730

# List all IAM policies
gcloud projects get-iam-policy ccibt-hack25ww7-730

# List all storage buckets
gcloud storage buckets list --project=ccibt-hack25ww7-730

# List all BigQuery datasets
bq ls --project_id=ccibt-hack25ww7-730
```

---

## 2. Regional Standards

### 2.1 Primary Region: us-central1

**Principle**: All GCP resources MUST be deployed in us-central1 unless technically impossible.

#### Supported Services in us-central1
- ✅ Vertex AI (all features)
- ✅ Cloud Run
- ✅ Cloud Functions (2nd gen)
- ✅ BigQuery
- ✅ Cloud Storage
- ✅ Gemini API
- ✅ Cloud Monitoring
- ✅ Cloud Logging

#### Multi-Region Exceptions
- **Cloud Storage**: Use `US` multi-region for high availability data
- **BigQuery**: Use `US` for datasets requiring multi-region access
- **Spanner**: Use `nam3` if global distribution needed

#### Configuration Standard
```python
# Python configuration
GCP_REGION = "us-central1"
GCP_ZONE = "us-central1-a"  # Primary zone
GCP_ZONE_BACKUP = "us-central1-b"  # Backup zone

# Terraform configuration
variable "region" {
  type    = string
  default = "us-central1"
}

variable "zone" {
  type    = string
  default = "us-central1-a"
}
```

---

## 3. AI Development Standards

### 3.1 ADK (Agent Development Kit) as Primary Tool

**Principle**: ADK MUST be used for all AI agent development unless technically infeasible.

#### When to Use ADK
- ✅ Building conversational AI agents
- ✅ Multi-step reasoning and planning
- ✅ Tool/function calling for external integrations
- ✅ Context management and memory
- ✅ Agent orchestration and workflows
- ✅ Integration with Vertex AI and Gemini

#### When ADK Cannot Be Used (Exceptions Required)
If ADK cannot be used, document the reason in code comments and architecture docs:

```python
# EXCEPTION: Using custom TensorFlow model instead of ADK
# REASON: Requires specialized time-series anomaly detection 
#         with custom LSTM architecture not supported by ADK
# APPROVED BY: [Team Lead Name]
# DATE: [YYYY-MM-DD]
```

#### Valid Exception Reasons
1. **Performance Requirements**: Sub-millisecond latency requirements that ADK cannot meet
2. **Custom Model Architecture**: Specialized ML models (e.g., custom LSTM, Transformer variants)
3. **Legacy Integration**: Must integrate with existing non-ADK systems
4. **Resource Constraints**: Memory/compute limitations in specific environments
5. **Feature Gap**: Required functionality not yet available in ADK

#### ADK Integration Pattern
```python
from google.cloud import aiplatform
from vertexai.preview import reasoning_engines

# Initialize ADK agent
agent = reasoning_engines.LangchainAgent(
    model="gemini-1.5-pro",
    tools=[
        analyze_volume_spike,
        query_finops_data,
        correlate_workload_metrics,
        generate_recommendations
    ],
    agent_executor_kwargs={
        "return_intermediate_steps": True,
        "max_iterations": 10
    }
)

# Deploy to Vertex AI
deployed_agent = reasoning_engines.ReasoningEngine.create(
    agent,
    requirements=["langchain", "google-cloud-bigquery"],
    display_name="anomaly-detection-agent",
    description="Agent for analyzing volume spikes and correlations"
)
```

---

## 4. Solution Architecture Standards

### 4.1 Anomaly Detection System Components

#### Core Components
1. **Data Ingestion Layer**
   - BigQuery for FinOps reports storage
   - Cloud Storage for raw workload metrics
   - Pub/Sub for real-time data streaming

2. **Processing Layer**
   - Cloud Functions for data preprocessing
   - Dataflow for batch processing (if needed)
   - Vertex AI Pipelines for ML workflows

3. **AI/ML Layer**
   - ADK Agent for orchestration and reasoning
   - Vertex AI for custom anomaly detection models
   - Gemini for natural language explanations

4. **API Layer**
   - Cloud Run for REST API endpoints
   - API Gateway for external access
   - Cloud Endpoints for API management

5. **Monitoring Layer**
   - Cloud Monitoring for metrics
   - Cloud Logging for centralized logs
   - Cloud Trace for distributed tracing

### 4.2 Data Source Integration Standards

#### FinOps Reports Integration
```python
# Standard schema for FinOps data
FINOPS_SCHEMA = {
    "timestamp": "TIMESTAMP",
    "resource_id": "STRING",
    "resource_type": "STRING",
    "cost": "FLOAT64",
    "usage_amount": "FLOAT64",
    "usage_unit": "STRING",
    "project_id": "STRING",
    "labels": "JSON"
}

# BigQuery table naming
# Format: {dataset}.finops_{report_type}_{YYYYMM}
# Example: analytics.finops_compute_202412
```

#### Workload Metrics Integration
```python
# Standard schema for workload metrics
WORKLOAD_SCHEMA = {
    "timestamp": "TIMESTAMP",
    "workload_id": "STRING",
    "workload_name": "STRING",
    "metric_type": "STRING",  # cpu, memory, requests, etc.
    "metric_value": "FLOAT64",
    "resource_id": "STRING",
    "namespace": "STRING",
    "labels": "JSON"
}

# Cloud Storage path structure
# gs://{bucket}/workload-metrics/{YYYY}/{MM}/{DD}/{workload_id}/metrics.json
```

### 4.3 Anomaly Detection Standards

#### Statistical Methods
- **Z-Score**: For detecting outliers in normal distributions
- **IQR Method**: For robust outlier detection
- **Moving Average**: For trend-based anomaly detection
- **Seasonal Decomposition**: For time-series with seasonality

#### ML-Based Methods
- **Isolation Forest**: For multivariate anomaly detection
- **LSTM Autoencoders**: For time-series anomaly detection
- **Prophet**: For forecasting and anomaly detection in time-series

#### Threshold Configuration
```python
# Anomaly severity levels
ANOMALY_THRESHOLDS = {
    "critical": 3.0,    # 3+ standard deviations
    "high": 2.5,        # 2.5-3 standard deviations
    "medium": 2.0,      # 2-2.5 standard deviations
    "low": 1.5          # 1.5-2 standard deviations
}

# Minimum confidence for reporting
MIN_CONFIDENCE = 0.75  # 75% confidence threshold
```

---

## 5. Development Workflow Standards

### 5.1 Environment Strategy

#### Environments
1. **Development (dev)**
   - Purpose: Active development and testing
   - Data: Synthetic or anonymized data
   - Cost: Minimal resources, auto-shutdown enabled

2. **Production (prod)**
   - Purpose: Live hackathon demo
   - Data: Real or realistic demo data
   - Cost: Optimized for performance

#### Environment Configuration
```bash
# .env.dev
GCP_PROJECT_ID=ccibt-hack25ww7-730
GCP_REGION=us-central1
ENVIRONMENT=dev
LOG_LEVEL=DEBUG

# .env.prod
GCP_PROJECT_ID=ccibt-hack25ww7-730
GCP_REGION=us-central1
ENVIRONMENT=prod
LOG_LEVEL=INFO
```

### 5.2 Git Workflow

#### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature development
- `hotfix/*`: Emergency fixes

#### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(anomaly-detection): add correlation analysis

Implement statistical correlation between volume spikes
and workload migrations using Pearson coefficient.

Closes #123
```

### 5.3 Code Quality Standards

#### Python Standards
- **Style Guide**: PEP 8
- **Type Hints**: Required for all functions
- **Docstrings**: Google style docstrings
- **Linting**: Use `ruff` or `pylint`
- **Formatting**: Use `black` with line length 100

#### Example
```python
from typing import List, Dict, Optional
from datetime import datetime

def analyze_volume_spike(
    metric_data: List[Dict[str, float]],
    threshold: float = 2.0,
    window_size: int = 24
) -> Optional[Dict[str, any]]:
    """Analyze volume spike in metric data.
    
    Args:
        metric_data: List of metric dictionaries with timestamp and value
        threshold: Z-score threshold for anomaly detection
        window_size: Rolling window size in hours
        
    Returns:
        Dictionary containing anomaly details or None if no anomaly detected
        
    Raises:
        ValueError: If metric_data is empty or invalid
    """
    if not metric_data:
        raise ValueError("metric_data cannot be empty")
    
    # Implementation here
    pass
```

### 5.4 Testing Standards

#### Test Coverage Requirements
- **Unit Tests**: Minimum 80% coverage
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user workflows

#### Test Structure
```
tests/
├── unit/
│   ├── test_anomaly_detection.py
│   ├── test_correlation.py
│   └── test_data_processing.py
├── integration/
│   ├── test_bigquery_integration.py
│   ├── test_vertex_ai_integration.py
│   └── test_api_endpoints.py
└── e2e/
    └── test_anomaly_workflow.py
```

---

## 6. API Standards

### 6.1 REST API Design

#### Endpoint Naming
- Use nouns, not verbs
- Use plural forms
- Use kebab-case for multi-word resources

```
GET    /api/v1/anomalies
GET    /api/v1/anomalies/{id}
POST   /api/v1/anomalies/analyze
GET    /api/v1/volume-spikes
POST   /api/v1/correlations/compute
```

#### Request/Response Format
```json
// Request
{
  "data": {
    "metric_type": "compute_usage",
    "time_range": {
      "start": "2024-12-01T00:00:00Z",
      "end": "2024-12-15T23:59:59Z"
    },
    "filters": {
      "project_id": "ccibt-hack25ww7-730",
      "resource_type": "compute_instance"
    }
  }
}

// Response
{
  "status": "success",
  "data": {
    "anomalies": [
      {
        "id": "anom-123",
        "timestamp": "2024-12-10T14:30:00Z",
        "severity": "high",
        "confidence": 0.92,
        "metric_value": 1250.5,
        "expected_value": 450.2,
        "deviation": 2.8,
        "explanation": "Detected 178% increase in compute usage...",
        "correlations": [
          {
            "type": "workload_migration",
            "confidence": 0.85,
            "details": "Migration of workload-xyz started at 14:15"
          }
        ],
        "recommendations": [
          "Review migration schedule for workload-xyz",
          "Consider scaling resources proactively"
        ]
      }
    ]
  },
  "metadata": {
    "request_id": "req-abc-123",
    "timestamp": "2024-12-16T13:30:00Z",
    "processing_time_ms": 245
  }
}
```

### 6.2 Error Handling

#### Standard Error Response
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid time range specified",
    "details": {
      "field": "time_range.start",
      "reason": "Start time cannot be in the future"
    }
  },
  "metadata": {
    "request_id": "req-abc-123",
    "timestamp": "2024-12-16T13:30:00Z"
  }
}
```

#### Error Codes
- `INVALID_REQUEST`: 400 - Client error in request
- `UNAUTHORIZED`: 401 - Authentication required
- `FORBIDDEN`: 403 - Insufficient permissions
- `NOT_FOUND`: 404 - Resource not found
- `RATE_LIMIT_EXCEEDED`: 429 - Too many requests
- `INTERNAL_ERROR`: 500 - Server error
- `SERVICE_UNAVAILABLE`: 503 - Temporary unavailability

---

## 7. Security Standards

### 7.1 Authentication & Authorization

#### Service Accounts
- Use Workload Identity for GKE workloads
- Use service account keys only when absolutely necessary
- Rotate service account keys every 90 days
- Follow principle of least privilege

#### IAM Roles
```hcl
# Terraform example
resource "google_project_iam_member" "agent_bigquery_reader" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.agent.email}"
}
```

### 7.2 Data Security

#### Encryption
- **At Rest**: Use Google-managed encryption keys (default)
- **In Transit**: TLS 1.3 for all communications
- **Sensitive Data**: Use Cloud KMS for application-level encryption

#### Data Classification
- **Public**: No restrictions (documentation, public APIs)
- **Internal**: Project team only (development data)
- **Confidential**: Restricted access (production data, credentials)

### 7.3 Secrets Management

#### Standards
- Store secrets in Secret Manager
- Never commit secrets to Git
- Use environment variables for runtime configuration
- Rotate secrets regularly

```python
from google.cloud import secretmanager

def get_secret(secret_id: str, version: str = "latest") -> str:
    """Retrieve secret from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/ccibt-hack25ww7-730/secrets/{secret_id}/versions/{version}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

---

## 8. Monitoring & Observability Standards

### 8.1 Logging Standards

#### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical issues requiring immediate attention

#### Structured Logging
```python
import logging
import json
from datetime import datetime

def log_structured(level: str, message: str, **kwargs):
    """Log structured JSON messages."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "project_id": "ccibt-hack25ww7-730",
        **kwargs
    }
    print(json.dumps(log_entry))

# Usage
log_structured(
    "INFO",
    "Anomaly detected",
    anomaly_id="anom-123",
    severity="high",
    confidence=0.92
)
```

### 8.2 Metrics Standards

#### Key Metrics to Track
1. **System Metrics**
   - API response time (p50, p95, p99)
   - Error rate
   - Request throughput
   - Resource utilization (CPU, memory)

2. **Business Metrics**
   - Anomalies detected per hour
   - Average time to root cause identification
   - Correlation accuracy
   - User satisfaction score

3. **Cost Metrics**
   - API call costs
   - Compute costs
   - Storage costs
   - Total cost per analysis

#### Custom Metrics
```python
from google.cloud import monitoring_v3

def record_metric(metric_type: str, value: float, labels: dict):
    """Record custom metric to Cloud Monitoring."""
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/ccibt-hack25ww7-730"
    
    series = monitoring_v3.TimeSeries()
    series.metric.type = f"custom.googleapis.com/{metric_type}"
    series.metric.labels.update(labels)
    
    point = monitoring_v3.Point()
    point.value.double_value = value
    point.interval.end_time.seconds = int(time.time())
    
    series.points = [point]
    client.create_time_series(name=project_name, time_series=[series])
```

### 8.3 Alerting Standards

#### Alert Severity Levels
- **P0 (Critical)**: System down, immediate response required
- **P1 (High)**: Major functionality impaired, response within 1 hour
- **P2 (Medium)**: Minor functionality impaired, response within 4 hours
- **P3 (Low)**: Informational, response within 24 hours

#### Alert Channels
- Email: For all severity levels
- Slack: For P0 and P1
- PagerDuty: For P0 only (if configured)

---

## 9. Documentation Standards

### 9.1 Required Documentation

#### Code Documentation
- README.md in every major directory
- Inline comments for complex logic
- API documentation (OpenAPI/Swagger)
- Architecture diagrams (Mermaid or draw.io)

#### Architecture Documentation
```
docs/
├── architecture/
│   ├── system-overview.md
│   ├── data-flow.md
│   ├── component-diagram.md
│   └── deployment-diagram.md
├── api/
│   ├── openapi.yaml
│   └── api-guide.md
├── development/
│   ├── setup-guide.md
│   ├── testing-guide.md
│   └── deployment-guide.md
└── operations/
    ├── runbook.md
    ├── troubleshooting.md
    └── monitoring-guide.md
```

### 9.2 README Template

```markdown
# Component Name

## Overview
Brief description of the component and its purpose.

## Architecture
High-level architecture diagram and explanation.

## Prerequisites
- Python 3.14+
- GCP Project: ccibt-hack25ww7-730
- Required APIs enabled

## Setup
Step-by-step setup instructions.

## Usage
Examples of how to use the component.

## Configuration
Environment variables and configuration options.

## Testing
How to run tests.

## Deployment
Deployment instructions.

## Monitoring
Key metrics and dashboards.

## Troubleshooting
Common issues and solutions.
```

---

## 10. Cost Optimization Standards

### 10.1 Cost Management

#### Budget Alerts
- Set budget alerts at 50%, 75%, 90%, and 100%
- Review costs weekly during development
- Optimize before production deployment

#### Resource Optimization
- Use committed use discounts for predictable workloads
- Enable autoscaling for variable workloads
- Use preemptible VMs for batch processing
- Implement lifecycle policies for Cloud Storage
- Set TTL for BigQuery tables

#### Cost Tracking
```python
# Tag all resources with cost tracking labels
labels = {
    "environment": "dev",
    "component": "anomaly-detection",
    "cost-center": "hackathon",
    "owner": "team-name"
}
```

### 10.2 Resource Cleanup

#### Automated Cleanup
- Delete dev resources after 7 days of inactivity
- Archive logs older than 30 days
- Delete temporary BigQuery tables after 24 hours

```bash
# Cleanup script example
gcloud compute instances list \
  --filter="labels.environment=dev AND creationTimestamp<-P7D" \
  --format="value(name)" | \
  xargs -I {} gcloud compute instances delete {} --quiet
```

---

## 11. Compliance & Best Practices

### 11.1 Data Privacy

#### PII Handling
- Identify and classify PII in data sources
- Implement data anonymization for non-production environments
- Use DLP API for sensitive data detection
- Document data retention policies

### 11.2 Disaster Recovery

#### Backup Strategy
- Daily backups of BigQuery datasets
- Versioning enabled for Cloud Storage buckets
- Terraform state backup in separate bucket
- Document recovery procedures

#### RTO/RPO Targets
- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 24 hours

---

## 12. Hackathon-Specific Guidelines

### 12.1 Demo Preparation

#### Demo Data
- Prepare realistic demo datasets
- Include various anomaly scenarios
- Document data generation process
- Test demo flow multiple times

#### Presentation Materials
- Architecture diagram
- Live demo script
- Backup screenshots/videos
- ROI calculations (time saved)

### 12.2 Judging Criteria Alignment

#### Innovation
- Highlight unique AI/ML approaches
- Demonstrate ADK capabilities
- Show advanced correlation techniques

#### Technical Excellence
- Clean, well-documented code
- Proper use of GCP services
- Scalable architecture
- Security best practices

#### Business Impact
- Quantify time savings (hours → minutes)
- Show cost reduction potential
- Demonstrate actionable insights
- User-friendly explanations

#### Presentation
- Clear problem statement
- Compelling demo
- Technical depth
- Q&A preparation

---

## 13. Quick Reference

### 13.1 Essential Commands

```bash
# Terraform
terraform init
terraform plan
terraform apply
terraform destroy

# GCP
gcloud config set project ccibt-hack25ww7-730
gcloud services enable <service-name>
gcloud auth application-default login

# Python
python -m venv gcp-ai-env
.\gcp-ai-env\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest tests/

# Git
git checkout -b feature/anomaly-detection
git commit -m "feat(detection): add spike analysis"
git push origin feature/anomaly-detection
```

### 13.2 Important Links

- **GCP Console**: https://console.cloud.google.com/
- **Project**: https://console.cloud.google.com/home/dashboard?project=ccibt-hack25ww7-730
- **Vertex AI**: https://console.cloud.google.com/vertex-ai?project=ccibt-hack25ww7-730
- **BigQuery**: https://console.cloud.google.com/bigquery?project=ccibt-hack25ww7-730
- **Cloud Storage**: https://console.cloud.google.com/storage/browser?project=ccibt-hack25ww7-730

---

## Document Version

- **Version**: 1.0
- **Last Updated**: 2024-12-16
- **Maintained By**: Hackathon Team
- **Review Cycle**: Weekly during development

---

## Approval & Sign-off

This standards document must be reviewed and approved before implementation begins.

- [ ] Technical Lead Review
- [ ] Architecture Review
- [ ] Security Review
- [ ] Cost Review
- [ ] Team Acknowledgment

---

*This document is a living standard and should be updated as the project evolves.*