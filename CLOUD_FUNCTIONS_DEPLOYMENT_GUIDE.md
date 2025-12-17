# Cloud Functions Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the Baseline Calculator and Analysis Agent as Google Cloud Functions using the Cloud Build portal.

## Prerequisites
- GCP Project: `ccibt-hack25ww7-730`
- Region: `us-central1`
- GitHub repositories already connected and updated with Cloud Function code

## Repository Status
Both repositories have been updated with Cloud Function support:

1. **Baseline Service**: https://github.com/DeathWatcher118/Baseline2.git
   - Contains `main.py` with `calculate_baseline()` and `health()` functions
   - Updated `requirements.txt` with `functions-framework==3.*`
   - Includes `.gcloudignore` for deployment optimization

2. **Analysis Agent**: https://github.com/DeathWatcher118/AnalysisAgent.git
   - Contains `main.py` with `analyze_anomaly()` and `health()` functions
   - Updated `requirements.txt` with `functions-framework==3.*`

## Deployment Instructions

### Option 1: Using Cloud Console (Recommended for First-Time Setup)

#### Deploy Baseline Calculator Function

1. **Navigate to Cloud Functions**
   - Go to: https://console.cloud.google.com/functions
   - Select project: `ccibt-hack25ww7-730`
   - Click "CREATE FUNCTION"

2. **Configure Function Basics**
   - **Environment**: 2nd gen
   - **Function name**: `baseline-calculator`
   - **Region**: `us-central1`

3. **Configure Trigger**
   - **Trigger type**: HTTPS
   - **Authentication**: Allow unauthenticated invocations (check the box)
   - Click "SAVE"

4. **Configure Runtime Settings** (Click "RUNTIME, BUILD, CONNECTIONS AND SECURITY SETTINGS")
   - **Memory**: 512 MB
   - **Timeout**: 300 seconds
   - **Maximum instances**: 100 (default)
   - **Minimum instances**: 0 (default)

5. **Configure Source Code**
   - **Source code**: Cloud Source repository (or GitHub if connected)
   - **Repository**: Select `Baseline2` repository
   - **Branch**: `main`
   - **Directory**: `/` (root)

6. **Configure Runtime**
   - **Runtime**: Python 3.14
   - **Entry point**: `calculate_baseline`
   - **Source code** will be automatically pulled from GitHub

7. **Deploy**
   - Click "DEPLOY"
   - Wait 3-5 minutes for deployment to complete
   - Note the function URL (will be displayed after deployment)

#### Deploy Analysis Agent Function

1. **Navigate to Cloud Functions**
   - Go to: https://console.cloud.google.com/functions
   - Click "CREATE FUNCTION"

2. **Configure Function Basics**
   - **Environment**: 2nd gen
   - **Function name**: `analysis-agent`
   - **Region**: `us-central1`

3. **Configure Trigger**
   - **Trigger type**: HTTPS
   - **Authentication**: Allow unauthenticated invocations (check the box)
   - Click "SAVE"

4. **Configure Runtime Settings**
   - **Memory**: 1 GB (Analysis Agent needs more memory for AI processing)
   - **Timeout**: 540 seconds (9 minutes - AI analysis can take longer)
   - **Maximum instances**: 100
   - **Minimum instances**: 0

5. **Configure Source Code**
   - **Source code**: Cloud Source repository (or GitHub if connected)
   - **Repository**: Select `AnalysisAgent` repository
   - **Branch**: `main`
   - **Directory**: `/` (root)

6. **Configure Runtime**
   - **Runtime**: Python 3.14
   - **Entry point**: `analyze_anomaly`

7. **Deploy**
   - Click "DEPLOY"
   - Wait 3-5 minutes for deployment
   - Note the function URL

### Option 2: Using Cloud Build Triggers (For Continuous Deployment)

#### Setup Build Trigger for Baseline Calculator

1. **Navigate to Cloud Build Triggers**
   - Go to: https://console.cloud.google.com/cloud-build/triggers
   - Click "CREATE TRIGGER"

2. **Configure Trigger**
   - **Name**: `deploy-baseline-calculator`
   - **Event**: Push to a branch
   - **Source**: Connect your GitHub repository `Baseline2`
   - **Branch**: `^main$`

3. **Configuration**
   - **Type**: Cloud Build configuration file (yaml or json)
   - **Location**: Repository
   - **Cloud Build configuration file location**: `cloudbuild.yaml`

4. **Create cloudbuild.yaml** (if not exists)
   ```yaml
   steps:
     - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
       args:
         - gcloud
         - functions
         - deploy
         - baseline-calculator
         - --gen2
         - --runtime=python314
         - --region=us-central1
         - --source=.
         - --entry-point=calculate_baseline
         - --trigger-http
         - --allow-unauthenticated
         - --memory=512MB
         - --timeout=300s
   ```

5. **Save Trigger**
   - Now every push to `main` branch will automatically deploy the function

#### Setup Build Trigger for Analysis Agent

1. **Create Trigger**
   - Name: `deploy-analysis-agent`
   - Event: Push to branch `main`
   - Source: `AnalysisAgent` repository

2. **Create cloudbuild.yaml**
   ```yaml
   steps:
     - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
       args:
         - gcloud
         - functions
         - deploy
         - analysis-agent
         - --gen2
         - --runtime=python314
         - --region=us-central1
         - --source=.
         - --entry-point=analyze_anomaly
         - --trigger-http
         - --allow-unauthenticated
         - --memory=1GB
         - --timeout=540s
   ```

### Option 3: Using gcloud CLI (Command Line)

If you prefer command-line deployment:

```bash
# Deploy Baseline Calculator
cd baseline-service
gcloud functions deploy baseline-calculator \
  --gen2 \
  --runtime=python314 \
  --region=us-central1 \
  --source=. \
  --entry-point=calculate_baseline \
  --trigger-http \
  --allow-unauthenticated \
  --project=ccibt-hack25ww7-730 \
  --memory=512MB \
  --timeout=300s

# Deploy Analysis Agent
cd ../analysis-agent
gcloud functions deploy analysis-agent \
  --gen2 \
  --runtime=python314 \
  --region=us-central1 \
  --source=. \
  --entry-point=analyze_anomaly \
  --trigger-http \
  --allow-unauthenticated \
  --project=ccibt-hack25ww7-730 \
  --memory=1GB \
  --timeout=540s
```

## Testing the Functions

### Test Baseline Calculator

```bash
# Health check
curl https://us-central1-ccibt-hack25ww7-730.cloudfunctions.net/baseline-calculator

# Calculate baseline
curl -X POST https://us-central1-ccibt-hack25ww7-730.cloudfunctions.net/baseline-calculator \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "cpu_usage",
    "metric_column": "average_usage",
    "source_table": "ccibt-hack25ww7-730.hackaton.borg_traces_data",
    "lookback_days": 30,
    "calculation_method": "simple_stats"
  }'
```

### Test Analysis Agent

```bash
# Health check
curl https://us-central1-ccibt-hack25ww7-730.cloudfunctions.net/analysis-agent

# Analyze anomaly
curl -X POST https://us-central1-ccibt-hack25ww7-730.cloudfunctions.net/analysis-agent \
  -H "Content-Type: application/json" \
  -d '{
    "anomaly_id": "test-001",
    "metric_name": "cpu_usage",
    "timestamp": "2024-01-15T10:30:00Z",
    "actual_value": 95.5,
    "expected_value": 45.2,
    "deviation": 50.3,
    "severity": "high",
    "detection_method": "z_score",
    "z_score": 4.5
  }'
```

## Troubleshooting

### Common Issues

1. **Function fails to start**
   - Check logs: https://console.cloud.google.com/logs
   - Verify `requirements.txt` has correct formatting
   - Ensure `functions-framework` is included

2. **Import errors**
   - Verify all dependencies are in `requirements.txt`
   - Check that `src/` directory structure is correct
   - Ensure `__init__.py` files exist in all packages

3. **Timeout errors**
   - Increase timeout in function configuration
   - For Analysis Agent, use 540s (9 minutes)
   - Check if BigQuery queries are optimized

4. **Memory errors**
   - Increase memory allocation
   - Baseline Calculator: 512MB should be sufficient
   - Analysis Agent: Use 1GB or more

5. **Authentication errors**
   - Verify service account has necessary permissions
   - Check BigQuery access permissions
   - Ensure Vertex AI API is enabled

## Required GCP APIs

Ensure these APIs are enabled in your project:

```bash
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

## Service Account Permissions

The Cloud Functions service account needs these roles:
- `roles/bigquery.dataViewer` - Read BigQuery data
- `roles/bigquery.jobUser` - Run BigQuery queries
- `roles/aiplatform.user` - Use Vertex AI
- `roles/storage.objectViewer` - Read from Cloud Storage (if needed)

## Monitoring and Logs

- **Function Logs**: https://console.cloud.google.com/functions/list
- **Cloud Build Logs**: https://console.cloud.google.com/cloud-build/builds
- **Error Reporting**: https://console.cloud.google.com/errors

## Next Steps

After successful deployment:

1. **Create BigQuery Table**
   - Run `sql/create_anomaly_analysis_table.sql`
   - This stores analysis results and user feedback

2. **Test End-to-End Flow**
   - Calculate baseline → Detect anomaly → Analyze anomaly
   - Verify data is persisted in BigQuery

3. **Set Up Monitoring**
   - Create alerts for function failures
   - Monitor execution times and costs
   - Track false positive rates

4. **Implement Notification System**
   - Build separate service to monitor BigQuery
   - Send alerts based on anomaly severity
   - Route to appropriate channels (email, Slack, etc.)

## Cost Optimization

- Use minimum instances = 0 to avoid idle costs
- Set appropriate memory limits (don't over-provision)
- Monitor invocation counts and optimize as needed
- Consider using Cloud Scheduler for periodic tasks instead of always-on services

## Support

For issues or questions:
- Check Cloud Functions documentation: https://cloud.google.com/functions/docs
- Review Cloud Build documentation: https://cloud.google.com/build/docs
- Check project logs and error reporting in GCP Console