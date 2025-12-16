# Hackathon Project

Clean project workspace ready for development.

## Environment Setup

### Python Environment
- **Python Version**: 3.14.0
- **Virtual Environment**: `gcp-ai-env`
- **Location**: `d:\Hackathon\gcp-ai-env`

### Activate Virtual Environment
```powershell
.\gcp-ai-env\Scripts\Activate.ps1
```

### Installed Packages (70+)
- Google Cloud AI Platform
- Google Cloud Vision, Language, Speech APIs
- Google Cloud Storage & BigQuery
- Google Generative AI (Gemini)
- PyTorch, scikit-learn, XGBoost, LightGBM
- Transformers, Datasets (Hugging Face)
- NumPy, Pandas, Matplotlib, Seaborn, Plotly

## GCP Configuration

### Account & Project
- **Account**: devstar7302@gcplab.me
- **Project ID**: ccibt-hack25ww7-730
- **Google Cloud SDK**: 549.0.1
- **SDK Location**: `C:\Users\Brian Onstot\AppData\Local\Google\Cloud SDK\google-cloud-sdk`

### Using gcloud CLI
```powershell
# Full path to gcloud
"C:\Users\Brian Onstot\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" --version

# Check authentication
"C:\Users\Brian Onstot\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" auth list

# View configuration
"C:\Users\Brian Onstot\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" config list
```

## Quick Start

1. Activate the virtual environment
2. Create your Python files
3. Start coding!

```powershell
# Activate environment
.\gcp-ai-env\Scripts\Activate.ps1

# Create your main file
New-Item main.py

# Run your code
python main.py
```

## Environment Variables

Copy `.env.example` to `.env` and configure:
```
GCP_PROJECT_ID=ccibt-hack25ww7-730
GCP_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json