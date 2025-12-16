# Deploy to GCP Using the Console (Web UI)

## Overview

This guide shows you how to deploy the Baseline Calculator and AI Agent to Google Cloud Platform using the **GCP Console** (web interface) instead of command line.

## Prerequisites

- GCP Account: `devstar7302@gcplab.me`
- Project: `ccibt-hack25ww7-730`
- Access to: https://console.cloud.google.com

## Deployment Options

### Option 1: Deploy via Cloud Build (Recommended)

#### Step 1: Navigate to Cloud Build
1. Go to: https://console.cloud.google.com/cloud-build/builds?project=ccibt-hack25ww7-730
2. Click **"CREATE TRIGGER"** or **"RUN"** button

#### Step 2: Create a Manual Build
1. Click **"RUN"** in the top menu
2. Select **"Cloud Build configuration file (yaml or json)"**
3. Choose **"Repository"** or **"Inline"**

#### Step 3: Configure Build (Inline Method)
1. Select **"Inline"** configuration
2. Paste this build configuration:

```yaml
steps:
  # Build the Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/ccibt-hack25ww7-730/baseline-calculator', '.']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/ccibt-hack25ww7-730/baseline-calculator']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'baseline-calculator'
      - '--image'
      - 'gcr.io/ccibt-hack25ww7-730/baseline-calculator'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '2'
      - '--timeout'
      - '900'

images:
  - 'gcr.io/ccibt-hack25ww7-730/baseline-calculator'
```

3. Click **"RUN"**

#### Step 4: Monitor Build
1. You'll be redirected to the build page
2. Watch the build logs in real-time
3. Wait for **"SUCCESS"** status (5-10 minutes)

---

### Option 2: Deploy via Cloud Run Directly

#### Step 1: Upload Code to Cloud Storage
1. Go to: https://console.cloud.google.com/storage/browser?project=ccibt-hack25ww7-730
2. Click **"CREATE BUCKET"**
3. Name: `baseline-calculator-source`
4. Region: `us-central1`
5. Click **"CREATE"**

#### Step 2: Upload Files
1. Open the bucket
2. Click **"UPLOAD FILES"** or **"UPLOAD FOLDER"**
3. Select your entire `d:/Hackathon` directory
4. Wait for upload to complete

#### Step 3: Deploy to Cloud Run
1. Go to: https://console.cloud.google.com/run?project=ccibt-hack25ww7-730
2. Click **"CREATE SERVICE"**
3. Select **"Continuously deploy new revisions from a source repository"**
4. Click **"SET UP WITH CLOUD BUILD"**

#### Step 4: Configure Service
**Container Settings:**
- **Service name**: `baseline-calculator`
- **Region**: `us-central1`
- **Authentication**: Allow unauthenticated invocations

**Container Configuration:**
- **Container image URL**: Will be built automatically
- **Container port**: `8080`

**Resources:**
- **Memory**: `2 GiB`
- **CPU**: `2`
- **Request timeout**: `900 seconds`
- **Maximum instances**: `10`

**Environment Variables:**
Click **"ADD VARIABLE"** for each:
```
GOOGLE_CLOUD_PROJECT = ccibt-hack25ww7-730
BIGQUERY_PROJECT_ID = ccibt-hack25ww7-730
BIGQUERY_DATASET = hackaton
```

5. Click **"CREATE"**

---

### Option 3: Deploy via Cloud Shell (In Browser)

#### Step 1: Open Cloud Shell
1. Go to: https://console.cloud.google.com
2. Click the **Cloud Shell icon** (>_) in the top right
3. Wait for shell to initialize

#### Step 2: Clone or Upload Code
```bash
# Option A: If code is in a Git repository
git clone YOUR_REPO_URL
cd YOUR_REPO_NAME

# Option B: Upload files manually
# Click the "Upload file" button in Cloud Shell
# Upload your project files
```

#### Step 3: Run Deployment Commands
```bash
# Set project
gcloud config set project ccibt-hack25ww7-730

# Build and deploy
gcloud builds submit --config=cloudbuild.yaml .
```

---

## Troubleshooting Failed Builds

### View Build Logs in Console

1. **Go to Cloud Build History**
   - URL: https://console.cloud.google.com/cloud-build/builds?project=ccibt-hack25ww7-730
   
2. **Find Your Build**
   - Look for build ID: `dcccef3a-cb6d-4f53-b40a-0b1dc6e5f723`
   - Status will show **"FAILED"** in red
   
3. **Click on the Build**
   - This opens the detailed build page
   
4. **View Logs**
   - Scroll down to see step-by-step logs
   - Look for **red error messages**
   - Common errors:
     - `ModuleNotFoundError`: Missing Python package
     - `Permission denied`: IAM permissions issue
     - `Dockerfile error`: Docker configuration problem
     - `Resource exhausted`: Need more memory/CPU

### Common Fixes

#### Error: "ModuleNotFoundError: No module named 'X'"
**Fix**: Add missing package to `requirements.txt`

#### Error: "Permission denied"
**Fix**: Enable required APIs:
1. Go to: https://console.cloud.google.com/apis/library?project=ccibt-hack25ww7-730
2. Search for and enable:
   - Cloud Build API
   - Cloud Run API
   - Container Registry API
   - Artifact Registry API

#### Error: "Dockerfile not found"
**Fix**: Ensure `Dockerfile` is in the root directory

#### Error: "Build timeout"
**Fix**: Increase timeout in `cloudbuild.yaml`:
```yaml
timeout: 1800s  # 30 minutes
```

---

## Verify Deployment

### Check Cloud Run Service

1. **Go to Cloud Run**
   - URL: https://console.cloud.google.com/run?project=ccibt-hack25ww7-730

2. **Find Your Service**
   - Look for `baseline-calculator`
   - Status should be **green checkmark** ✓

3. **Get Service URL**
   - Click on the service name
   - Copy the **URL** at the top (e.g., `https://baseline-calculator-xxxxx-uc.a.run.app`)

4. **Test the Service**
   - Open the URL in a browser
   - You should see a response (API endpoint or health check)

### Check Container Registry

1. **Go to Container Registry**
   - URL: https://console.cloud.google.com/gcr/images/ccibt-hack25ww7-730?project=ccibt-hack25ww7-730

2. **Verify Image**
   - Look for `baseline-calculator`
   - Should show recent timestamp

---

## Step-by-Step: Recommended Approach

### 🎯 Easiest Method: Cloud Build from Console

1. **Open Cloud Build**
   ```
   https://console.cloud.google.com/cloud-build/builds?project=ccibt-hack25ww7-730
   ```

2. **Click "RUN" button** (top right)

3. **Select "Cloud Build configuration file"**

4. **Choose "Repository" and connect your source**
   - If code is in GitHub/GitLab: Connect repository
   - If code is local: Use Cloud Shell to upload

5. **Or use "Inline" and paste the YAML** (from Option 1 above)

6. **Click "RUN"**

7. **Monitor progress** - Takes 5-10 minutes

8. **Check Cloud Run** for deployed service

---

## Alternative: Use Cloud Console's Built-in Editor

### Step 1: Open Cloud Shell Editor
1. Go to: https://console.cloud.google.com
2. Click **Cloud Shell icon** (>_)
3. Click **"Open Editor"** button
4. This opens a VS Code-like interface in your browser

### Step 2: Create Project Structure
1. Create folders: `src`, `docs`, etc.
2. Upload or paste your code files
3. Create `Dockerfile`, `cloudbuild.yaml`, `requirements.txt`

### Step 3: Deploy from Terminal
1. Click **"Open Terminal"** in the editor
2. Run:
```bash
gcloud config set project ccibt-hack25ww7-730
gcloud builds submit --config=cloudbuild.yaml .
```

---

## Quick Reference: Important URLs

| Resource | URL |
|----------|-----|
| **Cloud Build** | https://console.cloud.google.com/cloud-build/builds?project=ccibt-hack25ww7-730 |
| **Cloud Run** | https://console.cloud.google.com/run?project=ccibt-hack25ww7-730 |
| **Container Registry** | https://console.cloud.google.com/gcr/images/ccibt-hack25ww7-730 |
| **Cloud Storage** | https://console.cloud.google.com/storage/browser?project=ccibt-hack25ww7-730 |
| **IAM & Admin** | https://console.cloud.google.com/iam-admin/iam?project=ccibt-hack25ww7-730 |
| **APIs & Services** | https://console.cloud.google.com/apis/library?project=ccibt-hack25ww7-730 |
| **Cloud Shell** | https://console.cloud.google.com (click >_ icon) |

---

## Summary

**Recommended Path**:
1. Open Cloud Build in GCP Console
2. Click "RUN" → "Inline configuration"
3. Paste the YAML configuration
4. Click "RUN" and monitor
5. Check Cloud Run for deployed service

**Estimated Time**: 10-15 minutes total

**No command line needed** - everything can be done through the web interface!