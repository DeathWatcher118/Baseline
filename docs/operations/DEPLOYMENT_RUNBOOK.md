# Deployment Runbook

Complete deployment guide for the Anomaly Detection System.

## Overview

This runbook covers deployment procedures for:
- Infrastructure (Terraform)
- Application code (Cloud Run)
- ML models (Vertex AI)
- Monitoring and alerting

---

## Pre-Deployment Checklist

### Development Environment

- [ ] All tests passing (`pytest --cov=src tests/`)
- [ ] Code formatted (`black src/ tests/`)
- [ ] Linting passed (`ruff check src/ tests/`)
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] GCP authentication verified
- [ ] Terraform plan reviewed

### Infrastructure

- [ ] Terraform state bucket exists
- [ ] Required GCP APIs enabled
- [ ] IAM permissions configured
- [ ] Service accounts created
- [ ] Secrets stored in Secret Manager

### Code Quality

- [ ] Code review completed
- [ ] Security scan passed
- [ ] Performance testing done
- [ ] Integration tests passed
- [ ] API documentation updated

---

## Deployment Environments

### Development (dev)

- **Purpose**: Active development and testing
- **Auto-scaling**: Min 0, Max 5 instances
- **Data**: Synthetic/sample data
- **Cost**: Minimal, auto-shutdown enabled
- **Deployment**: Automatic on merge to `develop` branch

### Production (prod)

- **Purpose**: Live hackathon demo
- **Auto-scaling**: Min 1, Max 10 instances
- **Data**: Real/realistic demo data
- **Cost**: Optimized for performance
- **Deployment**: Manual approval required

---

## Phase 1: Infrastructure Deployment

### Step 1: Prepare Terraform

```bash
# Navigate to environment directory
cd terraform/environments/dev  # or prod

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive
```

### Step 2: Review Infrastructure Plan

```bash
# Generate plan
terraform plan -out=tfplan

# Review plan carefully
terraform show tfplan

# Check for:
# - Resource creation/modification/deletion
# - Cost implications
# - Security configurations
# - Network settings
```

### Step 3: Apply Infrastructure

```bash
# Apply changes
terraform apply tfplan

# Verify outputs
terraform output

# Expected outputs:
# - BigQuery dataset IDs
# - Cloud Storage bucket names
# - Cloud Run service URLs
# - Vertex AI region
```

### Step 4: Verify Infrastructure

```bash
# Verify BigQuery datasets
bq ls --project_id=ccibt-hack25ww7-730

# Verify Cloud Storage buckets
gcloud storage buckets list --project=ccibt-hack25ww7-730

# Verify Cloud Run services
gcloud run services list --project=ccibt-hack25ww7-730 --region=us-central1

# Check IAM permissions
gcloud projects get-iam-policy ccibt-hack25ww7-730
```

---

## Phase 2: Application Deployment

### Step 1: Build Docker Image

```bash
# Navigate to project root
cd d:/Hackathon

# Build Docker image
docker build -f docker/Dockerfile -t gcr.io/ccibt-hack25ww7-730/api:latest .

# Test image locally
docker run -p 8000:8000 \
  -e GCP_PROJECT_ID=ccibt-hack25ww7-730 \
  -e GCP_REGION=us-central1 \
  -e ENVIRONMENT=dev \
  gcr.io/ccibt-hack25ww7-730/api:latest

# Verify API is running
curl http://localhost:8000/health
```

### Step 2: Push Docker Image

```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Push image to Google Container Registry
docker push gcr.io/ccibt-hack25ww7-730/api:latest

# Verify image
gcloud container images list --repository=gcr.io/ccibt-hack25ww7-730
```

### Step 3: Deploy to Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy anomaly-detection-api \
  --image gcr.io/ccibt-hack25ww7-730/api:latest \
  --platform managed \
  --region us-central1 \
  --project ccibt-hack25ww7-730 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=ccibt-hack25ww7-730,GCP_REGION=us-central1,ENVIRONMENT=dev" \
  --memory 4Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 5 \
  --timeout 300s \
  --concurrency 80

# Get service URL
gcloud run services describe anomaly-detection-api \
  --region us-central1 \
  --project ccibt-hack25ww7-730 \
  --format 'value(status.url)'
```

### Step 4: Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe anomaly-detection-api \
  --region us-central1 \
  --project ccibt-hack25ww7-730 \
  --format 'value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health

# Test API docs
curl $SERVICE_URL/api/v1/docs

# Run smoke tests
pytest tests/e2e/test_deployment.py --service-url=$SERVICE_URL
```

---

## Phase 3: ML Model Deployment

### Step 1: Train Models

```bash
# Run training pipeline
python src/models/train_models.py \
  --project-id ccibt-hack25ww7-730 \
  --region us-central1 \
  --environment dev

# Verify training completed
# Check Vertex AI Pipelines in GCP Console
```

### Step 2: Register Models

```bash
# Upload models to Vertex AI Model Registry
python scripts/deployment/register_models.py \
  --project-id ccibt-hack25ww7-730 \
  --region us-central1 \
  --model-path models/isolation_forest/model_v1.pkl

# Verify model registration
gcloud ai models list \
  --region us-central1 \
  --project ccibt-hack25ww7-730
```

### Step 3: Deploy ADK Agent

```bash
# Deploy agent to Vertex AI
python src/agent/deploy_agent.py \
  --project-id ccibt-hack25ww7-730 \
  --region us-central1 \
  --environment dev

# Verify agent deployment
gcloud ai endpoints list \
  --region us-central1 \
  --project ccibt-hack25ww7-730
```

---

## Phase 4: Data Setup

### Step 1: Load Sample Data

```bash
# Load FinOps data
python scripts/data/load_finops_data.py \
  --project-id ccibt-hack25ww7-730 \
  --dataset finops_data \
  --table costs \
  --data-file data/samples/finops_sample.json

# Load workload metrics
python scripts/data/load_workload_metrics.py \
  --project-id ccibt-hack25ww7-730 \
  --dataset workload_metrics \
  --table metrics \
  --data-file data/samples/workload_sample.json

# Verify data loaded
bq query --project_id=ccibt-hack25ww7-730 \
  "SELECT COUNT(*) FROM finops_data.costs"
```

### Step 2: Create BigQuery Views

```bash
# Create materialized views for common queries
bq mk --use_legacy_sql=false \
  --materialized_view \
  --project_id=ccibt-hack25ww7-730 \
  --enable_refresh \
  --refresh_interval_ms=3600000 \
  finops_data.daily_costs_view \
  "SELECT 
    DATE(timestamp) as date,
    resource_type,
    SUM(cost) as total_cost,
    AVG(usage_amount) as avg_usage
  FROM finops_data.costs
  GROUP BY date, resource_type"
```

---

## Phase 5: Monitoring Setup

### Step 1: Configure Monitoring

```bash
# Create monitoring dashboard
gcloud monitoring dashboards create --config-from-file=config/monitoring.yaml

# Create alert policies
gcloud alpha monitoring policies create --policy-from-file=config/alerts.yaml
```

### Step 2: Set Up Logging

```bash
# Create log sink for errors
gcloud logging sinks create error-logs \
  storage.googleapis.com/ccibt-hack25ww7-730-logs \
  --log-filter='severity>=ERROR'

# Create log-based metrics
gcloud logging metrics create api_errors \
  --description="Count of API errors" \
  --log-filter='resource.type="cloud_run_revision" AND severity>=ERROR'
```

### Step 3: Configure Alerting

```bash
# Create notification channel
gcloud alpha monitoring channels create \
  --display-name="Email Alerts" \
  --type=email \
  --channel-labels=email_address=devstar7302@gcplab.me

# Verify alerts are configured
gcloud alpha monitoring policies list
```

---

## Phase 6: Post-Deployment Verification

### Automated Tests

```bash
# Run integration tests
pytest tests/integration/ --service-url=$SERVICE_URL

# Run end-to-end tests
pytest tests/e2e/ --service-url=$SERVICE_URL

# Run performance tests
python tests/performance/load_test.py --service-url=$SERVICE_URL
```

### Manual Verification

1. **API Health Check**
   ```bash
   curl $SERVICE_URL/health
   ```

2. **Test Anomaly Detection**
   ```bash
   curl -X POST $SERVICE_URL/api/v1/anomalies/detect \
     -H "Content-Type: application/json" \
     -d '{
       "data": {
         "metric_type": "compute_usage",
         "time_range": {
           "start": "2024-12-01T00:00:00Z",
           "end": "2024-12-15T23:59:59Z"
         }
       }
     }'
   ```

3. **Test Agent Query**
   ```bash
   curl -X POST $SERVICE_URL/api/v1/agent/query \
     -H "Content-Type: application/json" \
     -d '{
       "data": {
         "query": "What anomalies were detected today?"
       }
     }'
   ```

4. **Check Logs**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision" \
     --limit 50 \
     --project ccibt-hack25ww7-730
   ```

5. **Check Metrics**
   - Open Cloud Console
   - Navigate to Cloud Run → anomaly-detection-api
   - Check Metrics tab for:
     - Request count
     - Request latency
     - Error rate
     - Instance count

---

## Rollback Procedures

### Rollback Application

```bash
# List previous revisions
gcloud run revisions list \
  --service anomaly-detection-api \
  --region us-central1 \
  --project ccibt-hack25ww7-730

# Rollback to previous revision
gcloud run services update-traffic anomaly-detection-api \
  --to-revisions <previous-revision>=100 \
  --region us-central1 \
  --project ccibt-hack25ww7-730
```

### Rollback Infrastructure

```bash
# Navigate to terraform directory
cd terraform/environments/dev

# List state versions
gsutil ls -l gs://ccibt-hack25ww7-730-terraform-state/terraform/state/

# Download previous state
gsutil cp gs://ccibt-hack25ww7-730-terraform-state/terraform/state/<version> \
  terraform.tfstate

# Apply previous state
terraform apply
```

### Rollback Database Changes

```bash
# Restore BigQuery table from snapshot
bq cp \
  ccibt-hack25ww7-730:finops_data.costs@-3600000 \
  ccibt-hack25ww7-730:finops_data.costs_restored

# Verify restoration
bq query "SELECT COUNT(*) FROM finops_data.costs_restored"
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Code merged to appropriate branch
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Change request approved
- [ ] Deployment window scheduled
- [ ] Stakeholders notified

### During Deployment

- [ ] Infrastructure deployed successfully
- [ ] Application deployed successfully
- [ ] Models deployed successfully
- [ ] Data loaded successfully
- [ ] Monitoring configured
- [ ] Smoke tests passed

### Post-Deployment

- [ ] All services healthy
- [ ] Metrics being collected
- [ ] Logs flowing correctly
- [ ] Alerts configured
- [ ] Performance acceptable
- [ ] Documentation updated
- [ ] Stakeholders notified
- [ ] Deployment notes recorded

---

## Troubleshooting

### Common Issues

#### 1. Docker Build Fails

```bash
# Check Dockerfile syntax
docker build --no-cache -f docker/Dockerfile .

# Check for missing dependencies
pip install -r requirements.txt

# Verify base image
docker pull python:3.14-slim
```

#### 2. Cloud Run Deployment Fails

```bash
# Check service logs
gcloud run services logs read anomaly-detection-api \
  --region us-central1 \
  --project ccibt-hack25ww7-730

# Check IAM permissions
gcloud projects get-iam-policy ccibt-hack25ww7-730

# Verify image exists
gcloud container images list --repository=gcr.io/ccibt-hack25ww7-730
```

#### 3. API Returns 500 Errors

```bash
# Check application logs
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit 50 \
  --project ccibt-hack25ww7-730

# Check environment variables
gcloud run services describe anomaly-detection-api \
  --region us-central1 \
  --project ccibt-hack25ww7-730 \
  --format yaml

# Test locally
docker run -p 8000:8000 gcr.io/ccibt-hack25ww7-730/api:latest
```

#### 4. BigQuery Access Denied

```bash
# Check service account permissions
gcloud projects get-iam-policy ccibt-hack25ww7-730 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*"

# Grant necessary permissions
gcloud projects add-iam-policy-binding ccibt-hack25ww7-730 \
  --member="serviceAccount:anomaly-detection-sa@ccibt-hack25ww7-730.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
```

#### 5. Terraform Apply Fails

```bash
# Check state lock
terraform force-unlock <LOCK_ID>

# Refresh state
terraform refresh

# Re-initialize
terraform init -upgrade

# Validate configuration
terraform validate
```

---

## Maintenance Windows

### Scheduled Maintenance

- **Frequency**: Weekly (Sundays 2:00 AM - 4:00 AM EST)
- **Activities**:
  - Apply security patches
  - Update dependencies
  - Optimize database queries
  - Clean up old data
  - Review and update monitoring

### Emergency Maintenance

- **Trigger**: Critical security vulnerability or system failure
- **Process**:
  1. Assess impact and urgency
  2. Notify stakeholders
  3. Implement fix
  4. Test thoroughly
  5. Deploy to production
  6. Monitor closely
  7. Document incident

---

## Deployment Metrics

Track these metrics for each deployment:

- **Deployment Duration**: Time from start to completion
- **Downtime**: Any service interruption
- **Rollback Count**: Number of rollbacks required
- **Error Rate**: Post-deployment error rate
- **Performance**: Response time changes
- **Cost**: Deployment cost impact

---

## Contact Information

### Escalation Path

1. **Level 1**: Development Team
2. **Level 2**: Technical Lead
3. **Level 3**: Project Manager
4. **Level 4**: GCP Support

### Emergency Contacts

- **Technical Lead**: [Contact Info]
- **GCP Support**: https://cloud.google.com/support
- **On-Call**: [Rotation Schedule]

---

## Appendix

### Useful Commands

```bash
# View all Cloud Run services
gcloud run services list --project=ccibt-hack25ww7-730

# View service details
gcloud run services describe <service-name> \
  --region us-central1 \
  --project ccibt-hack25ww7-730

# View logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 100 \
  --project ccibt-hack25ww7-730

# View metrics
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_count"' \
  --project ccibt-hack25ww7-730

# Update service
gcloud run services update <service-name> \
  --set-env-vars KEY=VALUE \
  --region us-central1 \
  --project ccibt-hack25ww7-730
```

### Links

- **GCP Console**: https://console.cloud.google.com/
- **Cloud Run**: https://console.cloud.google.com/run?project=ccibt-hack25ww7-730
- **Vertex AI**: https://console.cloud.google.com/vertex-ai?project=ccibt-hack25ww7-730
- **BigQuery**: https://console.cloud.google.com/bigquery?project=ccibt-hack25ww7-730
- **Monitoring**: https://console.cloud.google.com/monitoring?project=ccibt-hack25ww7-730

---

**Document Version**: 1.0  
**Last Updated**: 2024-12-16  
**Maintained By**: Hackathon Team