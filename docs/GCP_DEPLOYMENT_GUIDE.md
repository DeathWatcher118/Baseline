# GCP Deployment Guide - Baseline Calculator

## Overview

This guide provides step-by-step instructions for deploying the AI-powered Baseline Calculator to Google Cloud Platform (GCP).

## Prerequisites

### Required Tools
- ✅ Google Cloud SDK installed
- ✅ Docker installed
- ✅ GCP project created (`ccibt-hack25ww7-730`)
- ✅ Billing enabled on GCP project
- ✅ Appropriate IAM permissions

### Required Permissions
- Cloud Run Admin
- Cloud Build Editor
- Container Registry Admin
- Vertex AI User
- BigQuery Data Editor

## Deployment Options

### Option 1: Automated Deployment (Recommended)

Use the provided deployment script for one-command deployment.

```bash
# Make script executable
chmod +x deploy_to_gcp.sh

# Run deployment
./deploy_to_gcp.sh
```

**What it does:**
1. Authenticates with GCP
2. Enables required APIs
3. Builds Docker image
4. Pushes to Container Registry
5. Deploys to Cloud Run
6. Provides service URL

**Time**: ~5-10 minutes

### Option 2: Manual Deployment

Follow these steps for manual control over the deployment process.

#### Step 1: Authenticate with GCP

```bash
# Login to GCP
gcloud auth login

# Set project
gcloud config set project ccibt-hack25ww7-730

# Verify authentication
gcloud auth list
```

#### Step 2: Enable Required APIs

```bash
# Enable Cloud Build
gcloud services enable cloudbuild.googleapis.com

# Enable Cloud Run
gcloud services enable run.googleapis.com

# Enable Container Registry
gcloud services enable containerregistry.googleapis.com

# Enable Vertex AI
gcloud services enable aiplatform.googleapis.com

# Enable BigQuery (if not already enabled)
gcloud services enable bigquery.googleapis.com
```

#### Step 3: Build Docker Image

```bash
# Build image
docker build -t gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest .

# Verify image
docker images | grep baseline-calculator
```

#### Step 4: Push to Container Registry

```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Push image
docker push gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest

# Verify push
gcloud container images list --repository=gcr.io/ccibt-hack25ww7-730
```

#### Step 5: Deploy to Cloud Run

```bash
# Deploy service
gcloud run deploy baseline-calculator \
    --image gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 900 \
    --set-env-vars "GCP_PROJECT_ID=ccibt-hack25ww7-730" \
    --set-env-vars "GCP_REGION=us-central1" \
    --set-env-vars "PYTHONUNBUFFERED=1"
```

**Configuration Explained:**
- `--memory 2Gi`: 2GB RAM for data processing
- `--cpu 2`: 2 vCPUs for parallel processing
- `--timeout 900`: 15 minutes max execution time
- `--allow-unauthenticated`: Public access (change for production)

#### Step 6: Verify Deployment

```bash
# Get service URL
gcloud run services describe baseline-calculator \
    --region us-central1 \
    --format 'value(status.url)'

# Check service status
gcloud run services list --region us-central1
```

## Post-Deployment Configuration

### Set Up Service Account (Recommended)

```bash
# Create service account
gcloud iam service-accounts create baseline-calculator-sa \
    --display-name="Baseline Calculator Service Account"

# Grant BigQuery permissions
gcloud projects add-iam-policy-binding ccibt-hack25ww7-730 \
    --member="serviceAccount:baseline-calculator-sa@ccibt-hack25ww7-730.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

# Grant Vertex AI permissions
gcloud projects add-iam-policy-binding ccibt-hack25ww7-730 \
    --member="serviceAccount:baseline-calculator-sa@ccibt-hack25ww7-730.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Update Cloud Run service to use service account
gcloud run services update baseline-calculator \
    --region us-central1 \
    --service-account baseline-calculator-sa@ccibt-hack25ww7-730.iam.gserviceaccount.com
```

### Configure Environment Variables

```bash
# Update service with additional env vars
gcloud run services update baseline-calculator \
    --region us-central1 \
    --update-env-vars "USE_AI_OPTIMIZATION=true" \
    --update-env-vars "AI_CONFIDENCE_THRESHOLD=0.75"
```

### Set Up Cloud Scheduler (Optional)

For automated daily baseline calculations:

```bash
# Create scheduler job
gcloud scheduler jobs create http baseline-daily-calculation \
    --location us-central1 \
    --schedule="0 2 * * *" \
    --uri="https://baseline-calculator-xxxxx.run.app/calculate" \
    --http-method=POST \
    --time-zone="America/New_York" \
    --description="Daily baseline calculation at 2 AM EST"
```

## Testing Deployment

### Test 1: Health Check

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe baseline-calculator --region us-central1 --format 'value(status.url)')

# Test health endpoint
curl ${SERVICE_URL}/health
```

### Test 2: Baseline Calculation

```bash
# Trigger baseline calculation
curl -X POST ${SERVICE_URL}/calculate

# Or with specific metric
curl -X POST ${SERVICE_URL}/calculate \
    -H "Content-Type: application/json" \
    -d '{"metric": "error_rate"}'
```

### Test 3: View Logs

```bash
# View recent logs
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=baseline-calculator" \
    --limit 50 \
    --format json

# Stream logs in real-time
gcloud logging tail \
    "resource.type=cloud_run_revision AND resource.labels.service_name=baseline-calculator"
```

## Monitoring & Observability

### Cloud Monitoring Dashboard

```bash
# Create monitoring dashboard
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json
```

### Set Up Alerts

```bash
# Alert on errors
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="Baseline Calculator Errors" \
    --condition-display-name="Error rate > 5%" \
    --condition-threshold-value=5 \
    --condition-threshold-duration=300s
```

### View Metrics

```bash
# View request count
gcloud monitoring time-series list \
    --filter='metric.type="run.googleapis.com/request_count"' \
    --format=json

# View latency
gcloud monitoring time-series list \
    --filter='metric.type="run.googleapis.com/request_latencies"' \
    --format=json
```

## Cost Optimization

### Current Configuration Costs

**Cloud Run:**
- Memory: 2GB × $0.0000025/GB-second
- CPU: 2 vCPU × $0.00002400/vCPU-second
- Requests: $0.40 per million requests

**Estimated Monthly Cost (Daily runs):**
- Execution: ~$5-10/month
- Vertex AI: ~$0.53/month
- BigQuery: Minimal (queries only)
- **Total: ~$6-11/month**

### Cost Reduction Tips

1. **Reduce Memory**: If not needed, reduce to 1GB
```bash
gcloud run services update baseline-calculator \
    --memory 1Gi --region us-central1
```

2. **Reduce CPU**: Use 1 vCPU if performance is acceptable
```bash
gcloud run services update baseline-calculator \
    --cpu 1 --region us-central1
```

3. **Disable AI**: Use rule-based for lower cost
```bash
gcloud run services update baseline-calculator \
    --update-env-vars "USE_AI_OPTIMIZATION=false" \
    --region us-central1
```

## Troubleshooting

### Issue: Deployment Fails

**Solution:**
```bash
# Check build logs
gcloud builds list --limit=5

# View specific build
gcloud builds log BUILD_ID
```

### Issue: Service Won't Start

**Solution:**
```bash
# Check service logs
gcloud logging read \
    "resource.type=cloud_run_revision" \
    --limit 100

# Check service configuration
gcloud run services describe baseline-calculator \
    --region us-central1
```

### Issue: Authentication Errors

**Solution:**
```bash
# Re-authenticate
gcloud auth application-default login

# Verify service account
gcloud run services describe baseline-calculator \
    --region us-central1 \
    --format='value(spec.template.spec.serviceAccountName)'
```

### Issue: Out of Memory

**Solution:**
```bash
# Increase memory
gcloud run services update baseline-calculator \
    --memory 4Gi --region us-central1
```

## Updating the Service

### Update Code

```bash
# Rebuild image
docker build -t gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest .

# Push new version
docker push gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest

# Deploy update
gcloud run deploy baseline-calculator \
    --image gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest \
    --region us-central1
```

### Update Configuration

```bash
# Update environment variables
gcloud run services update baseline-calculator \
    --update-env-vars "NEW_VAR=value" \
    --region us-central1

# Update resources
gcloud run services update baseline-calculator \
    --memory 4Gi \
    --cpu 4 \
    --region us-central1
```

## Rollback

### Rollback to Previous Version

```bash
# List revisions
gcloud run revisions list \
    --service baseline-calculator \
    --region us-central1

# Rollback to specific revision
gcloud run services update-traffic baseline-calculator \
    --to-revisions REVISION_NAME=100 \
    --region us-central1
```

## Cleanup

### Delete Service

```bash
# Delete Cloud Run service
gcloud run services delete baseline-calculator \
    --region us-central1

# Delete Docker images
gcloud container images delete gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest

# Delete scheduler job (if created)
gcloud scheduler jobs delete baseline-daily-calculation \
    --location us-central1
```

## Security Best Practices

### 1. Use Service Accounts
- Create dedicated service account
- Grant minimum required permissions
- Rotate credentials regularly

### 2. Enable Authentication
```bash
# Require authentication
gcloud run services update baseline-calculator \
    --no-allow-unauthenticated \
    --region us-central1
```

### 3. Use Secret Manager
```bash
# Store sensitive data in Secret Manager
gcloud secrets create baseline-api-key --data-file=api-key.txt

# Grant access to service account
gcloud secrets add-iam-policy-binding baseline-api-key \
    --member="serviceAccount:baseline-calculator-sa@ccibt-hack25ww7-730.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 4. Enable VPC Connector (Optional)
For private network access to resources.

## Next Steps

After successful deployment:

1. ✅ Verify baseline calculations work
2. ✅ Set up monitoring and alerts
3. ✅ Configure Cloud Scheduler for automation
4. ✅ Test AI optimization
5. ✅ Deploy detection module
6. ✅ Build API layer
7. ✅ Create dashboard

## Support

For issues or questions:
- Check logs: `gcloud logging read`
- View documentation: `docs/`
- GCP Support: https://cloud.google.com/support

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-16  
**Status:** Production Ready ✅