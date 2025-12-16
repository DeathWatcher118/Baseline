# Deploy Baseline Calculator to Google Cloud Platform (PowerShell)
# Usage: .\deploy_to_gcp.ps1

# Configuration
$PROJECT_ID = "ccibt-hack25ww7-730"
$REGION = "us-central1"
$SERVICE_NAME = "baseline-calculator"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deploying Baseline Calculator to GCP" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Service: $SERVICE_NAME"
Write-Host ""

# Step 1: Authenticate
Write-Host "[1/6] Checking GCP authentication..." -ForegroundColor Yellow
gcloud auth list
gcloud config set project $PROJECT_ID

# Step 2: Enable required APIs
Write-Host ""
Write-Host "[2/6] Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable aiplatform.googleapis.com

# Step 3: Build Docker image
Write-Host ""
Write-Host "[3/6] Building Docker image..." -ForegroundColor Yellow
docker build -t "${IMAGE_NAME}:latest" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed!" -ForegroundColor Red
    exit 1
}

# Step 4: Configure Docker for GCR
Write-Host ""
Write-Host "[4/6] Configuring Docker for GCR..." -ForegroundColor Yellow
gcloud auth configure-docker

# Step 5: Push to Container Registry
Write-Host ""
Write-Host "[5/6] Pushing image to Container Registry..." -ForegroundColor Yellow
docker push "${IMAGE_NAME}:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker push failed!" -ForegroundColor Red
    exit 1
}

# Step 6: Deploy to Cloud Run
Write-Host ""
Write-Host "[6/6] Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --image "${IMAGE_NAME}:latest" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 900 `
    --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID" `
    --set-env-vars "GCP_REGION=$REGION" `
    --set-env-vars "PYTHONUNBUFFERED=1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Cloud Run deployment failed!" -ForegroundColor Red
    exit 1
}

# Get service URL
Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Deployment Successful!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Green
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Cyan
Write-Host "  gcloud logging read `"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME`" --limit 50"
Write-Host ""
Write-Host "To trigger baseline calculation:" -ForegroundColor Cyan
Write-Host "  curl $SERVICE_URL/calculate"
Write-Host ""