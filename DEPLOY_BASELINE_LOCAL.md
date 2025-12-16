# Deploy Baseline Calculator - Build Locally, Push to GCP

This guide shows how to build the Docker image locally and push it to GCP Cloud Run.

## Prerequisites

- Docker Desktop installed and running
- gcloud CLI authenticated (`gcloud auth login`)
- Docker configured for GCP (`gcloud auth configure-docker`)

---

## Step-by-Step Deployment

### Step 1: Navigate to Project Directory

```bash
cd d:/Hackathon
```

### Step 2: Configure Docker for GCP Container Registry

```bash
gcloud auth configure-docker
```

This allows Docker to push images to Google Container Registry (gcr.io).

### Step 3: Build Docker Image Locally

```bash
docker build -f Dockerfile.baseline -t gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest .
```

**What this does:**
- Uses `Dockerfile.baseline` (baseline-only configuration)
- Tags image as `gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest`
- Builds from current directory (`.`)

**Expected output:**
```
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition from Dockerfile.baseline
 => => transferring dockerfile: 789B
 => [internal] load .dockerignore
 => [internal] load metadata for docker.io/library/python:3.14-slim
 ...
 => => naming to gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest
```

### Step 4: Test Image Locally (Optional)

```bash
docker run -p 8080:8080 -e GCP_PROJECT_ID=ccibt-hack25ww7-730 -e GCP_REGION=us-central1 gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest
```

Press `Ctrl+C` to stop when done testing.

### Step 5: Push Image to Google Container Registry

```bash
docker push gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest
```

**Expected output:**
```
The push refers to repository [gcr.io/ccibt-hack25ww7-730/baseline-calculator]
5f70bf18a086: Pushed
...
latest: digest: sha256:abc123... size: 2841
```

### Step 6: Deploy to Cloud Run

```bash
gcloud run deploy baseline-calculator \
  --image=gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --timeout=900 \
  --set-env-vars=GCP_PROJECT_ID=ccibt-hack25ww7-730,GCP_REGION=us-central1,PYTHONUNBUFFERED=1 \
  --project=ccibt-hack25ww7-730
```

**Expected output:**
```
Deploying container to Cloud Run service [baseline-calculator] in project [ccibt-hack25ww7-730] region [us-central1]
✓ Deploying new service... Done.
  ✓ Creating Revision...
  ✓ Routing traffic...
Done.
Service [baseline-calculator] revision [baseline-calculator-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://baseline-calculator-abc123-uc.a.run.app
```

---

## Complete Command Sequence

Copy and paste these commands in order:

```bash
# 1. Navigate to project
cd d:/Hackathon

# 2. Configure Docker for GCP
gcloud auth configure-docker

# 3. Build image locally
docker build -f Dockerfile.baseline -t gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest .

# 4. Push to Container Registry
docker push gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest

# 5. Deploy to Cloud Run
gcloud run deploy baseline-calculator \
  --image=gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --timeout=900 \
  --set-env-vars=GCP_PROJECT_ID=ccibt-hack25ww7-730,GCP_REGION=us-central1,PYTHONUNBUFFERED=1 \
  --project=ccibt-hack25ww7-730
```

---

## What Gets Deployed

**Included:**
- ✅ Baseline calculator (`src/baseline/calculator.py`)
- ✅ AI optimizer (`src/baseline/ai_optimizer.py`)
- ✅ Utilities (`src/utils/`)
- ✅ Configuration (`config.yaml`)
- ✅ Python dependencies (`requirements.txt`)

**Excluded:**
- ❌ AI agent (`src/agent/`)
- ❌ Data models (`src/models/`)
- ❌ SQL schemas
- ❌ Documentation
- ❌ Scripts

---

## Verify Deployment

### Check Service Status
```bash
gcloud run services describe baseline-calculator --region=us-central1 --project=ccibt-hack25ww7-730
```

### View Logs
```bash
gcloud run services logs read baseline-calculator --region=us-central1 --project=ccibt-hack25ww7-730
```

### Test Endpoint
```bash
curl https://baseline-calculator-<your-hash>-uc.a.run.app
```

---

## Troubleshooting

### Docker Build Fails
- Ensure Docker Desktop is running
- Check `Dockerfile.baseline` exists
- Verify you're in `d:/Hackathon` directory

### Push Fails (Authentication)
```bash
gcloud auth login
gcloud auth configure-docker
```

### Deploy Fails (Permissions)
```bash
gcloud auth application-default login
```

### Image Not Found
Verify image exists:
```bash
gcloud container images list --repository=gcr.io/ccibt-hack25ww7-730
```

---

## Update Deployment

To update after code changes:

```bash
# Rebuild with new code
docker build -f Dockerfile.baseline -t gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest .

# Push updated image
docker push gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest

# Redeploy (Cloud Run auto-detects new image)
gcloud run deploy baseline-calculator \
  --image=gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest \
  --region=us-central1 \
  --project=ccibt-hack25ww7-730
```

---

## Clean Up

### Delete Service
```bash
gcloud run services delete baseline-calculator --region=us-central1 --project=ccibt-hack25ww7-730
```

### Delete Image
```bash
gcloud container images delete gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest --quiet
```

---

## Benefits of Local Build

✅ **Test Before Deploy**: Verify image works locally
✅ **Faster Iteration**: No waiting for Cloud Build
✅ **Offline Development**: Build without internet
✅ **Debug Easier**: See build errors immediately
✅ **Control**: Full control over build process