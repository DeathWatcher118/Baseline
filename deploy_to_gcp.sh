#!/bin/bash
# Deploy Baseline Calculator to Google Cloud Platform
# Usage: ./deploy_to_gcp.sh

set -e  # Exit on error

# Configuration
PROJECT_ID="ccibt-hack25ww7-730"
REGION="us-central1"
SERVICE_NAME="baseline-calculator"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "========================================="
echo "Deploying Baseline Calculator to GCP"
echo "========================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Step 1: Authenticate
echo "[1/6] Authenticating with GCP..."
gcloud auth list
gcloud config set project ${PROJECT_ID}

# Step 2: Enable required APIs
echo ""
echo "[2/6] Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    aiplatform.googleapis.com

# Step 3: Build Docker image
echo ""
echo "[3/6] Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

# Step 4: Push to Container Registry
echo ""
echo "[4/6] Pushing image to Container Registry..."
docker push ${IMAGE_NAME}:latest

# Step 5: Deploy to Cloud Run
echo ""
echo "[5/6] Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 900 \
    --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID}" \
    --set-env-vars "GCP_REGION=${REGION}" \
    --set-env-vars "PYTHONUNBUFFERED=1"

# Step 6: Get service URL
echo ""
echo "[6/6] Deployment complete!"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo ""
echo "========================================="
echo "Deployment Successful!"
echo "========================================="
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "To view logs:"
echo "  gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}\" --limit 50"
echo ""
echo "To trigger baseline calculation:"
echo "  curl ${SERVICE_URL}/calculate"
echo ""