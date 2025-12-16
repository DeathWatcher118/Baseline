# Terraform Setup Guide

This guide provides the complete Terraform configuration structure for the Anomaly Detection System.

## Directory Structure to Create

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       ├── terraform.tfvars
│       └── backend.tf
├── modules/
│   ├── bigquery/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── cloud-storage/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── cloud-run/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── vertex-ai/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── monitoring/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── networking/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── scripts/
│   ├── inventory_gcp_resources.py
│   └── setup_state_bucket.sh
└── README.md
```

## File Contents

### environments/dev/backend.tf

```hcl
terraform {
  backend "gcs" {
    bucket = "ccibt-hack25ww7-730-terraform-state"
    prefix = "terraform/state/dev"
  }
}
```

### environments/dev/main.tf

```hcl
# Development Environment - Main Configuration

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
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Local variables
locals {
  environment = "dev"
  common_labels = {
    environment = local.environment
    project     = "hackathon-anomaly-detection"
    managed_by  = "terraform"
    cost_center = "hackathon"
  }
}

# BigQuery Module
module "bigquery" {
  source = "../../modules/bigquery"
  
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
  labels      = local.common_labels
  
  datasets = {
    finops_data = {
      dataset_id  = "finops_data"
      description = "FinOps cost and usage data"
      location    = "US"
    }
    workload_metrics = {
      dataset_id  = "workload_metrics"
      description = "Workload performance metrics"
      location    = "US"
    }
    anomaly_results = {
      dataset_id  = "anomaly_results"
      description = "Anomaly detection results"
      location    = "US"
    }
    correlations = {
      dataset_id  = "correlations"
      description = "Correlation analysis results"
      location    = "US"
    }
  }
}

# Cloud Storage Module
module "storage" {
  source = "../../modules/cloud-storage"
  
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
  labels      = local.common_labels
  
  buckets = {
    data = {
      name          = "${var.project_id}-${local.environment}-data"
      location      = "US"
      storage_class = "STANDARD"
      versioning    = true
      
      lifecycle_rules = [
        {
          action = {
            type = "Delete"
          }
          condition = {
            age = 90
          }
        }
      ]
    }
    
    models = {
      name          = "${var.project_id}-${local.environment}-models"
      location      = var.region
      storage_class = "STANDARD"
      versioning    = true
    }
  }
}

# Cloud Run Module
module "cloud_run" {
  source = "../../modules/cloud-run"
  
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
  labels      = local.common_labels
  
  services = {
    api = {
      name  = "anomaly-detection-api"
      image = "gcr.io/${var.project_id}/api:latest"
      
      resources = {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }
      
      scaling = {
        min_instance_count = 0  # Scale to zero in dev
        max_instance_count = 5
      }
      
      env_vars = [
        {
          name  = "ENVIRONMENT"
          value = local.environment
        },
        {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        },
        {
          name  = "GCP_REGION"
          value = var.region
        }
      ]
    }
  }
}

# Vertex AI Module
module "vertex_ai" {
  source = "../../modules/vertex-ai"
  
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
  labels      = local.common_labels
  
  enable_notebooks = true
  enable_pipelines = true
}

# Monitoring Module
module "monitoring" {
  source = "../../modules/monitoring"
  
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
  
  notification_channels = var.notification_channels
  
  alert_policies = {
    api_error_rate = {
      display_name = "API Error Rate High"
      conditions = [{
        display_name = "Error rate > 5%"
        threshold    = 0.05
      }]
    }
    
    api_latency = {
      display_name = "API Latency High"
      conditions = [{
        display_name = "P95 latency > 2s"
        threshold    = 2000
      }]
    }
  }
}

# Networking Module (Optional - for VPC)
module "networking" {
  source = "../../modules/networking"
  
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
  
  create_vpc = false  # Use default VPC in dev
}
```

### environments/dev/variables.tf

```hcl
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "ccibt-hack25ww7-730"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "notification_channels" {
  description = "Email addresses for monitoring alerts"
  type        = list(string)
  default     = []
}
```

### environments/dev/outputs.tf

```hcl
output "bigquery_datasets" {
  description = "BigQuery dataset IDs"
  value       = module.bigquery.dataset_ids
}

output "storage_buckets" {
  description = "Cloud Storage bucket names"
  value       = module.storage.bucket_names
}

output "cloud_run_urls" {
  description = "Cloud Run service URLs"
  value       = module.cloud_run.service_urls
}

output "vertex_ai_region" {
  description = "Vertex AI region"
  value       = module.vertex_ai.region
}
```

### environments/dev/terraform.tfvars

```hcl
# Development Environment Variables

project_id = "ccibt-hack25ww7-730"
region     = "us-central1"
zone       = "us-central1-a"

notification_channels = [
  "devstar7302@gcplab.me"
]
```

## Module Configurations

### modules/bigquery/main.tf

```hcl
resource "google_bigquery_dataset" "datasets" {
  for_each = var.datasets
  
  project    = var.project_id
  dataset_id = each.value.dataset_id
  location   = each.value.location
  
  description = each.value.description
  
  labels = var.labels
  
  delete_contents_on_destroy = var.environment == "dev" ? true : false
  
  access {
    role          = "OWNER"
    user_by_email = "devstar7302@gcplab.me"
  }
}

# Example table for FinOps data
resource "google_bigquery_table" "finops_costs" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.datasets["finops_data"].dataset_id
  table_id   = "costs"
  
  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }
  
  clustering = ["resource_type", "project_id"]
  
  schema = jsonencode([
    {
      name = "timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "resource_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "resource_type"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "cost"
      type = "FLOAT64"
      mode = "REQUIRED"
    },
    {
      name = "usage_amount"
      type = "FLOAT64"
      mode = "NULLABLE"
    },
    {
      name = "usage_unit"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "project_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "labels"
      type = "JSON"
      mode = "NULLABLE"
    }
  ])
  
  labels = var.labels
}
```

### modules/bigquery/variables.tf

```hcl
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default     = {}
}

variable "datasets" {
  description = "BigQuery datasets to create"
  type = map(object({
    dataset_id  = string
    description = string
    location    = string
  }))
}
```

### modules/bigquery/outputs.tf

```hcl
output "dataset_ids" {
  description = "Map of dataset names to IDs"
  value = {
    for k, v in google_bigquery_dataset.datasets : k => v.dataset_id
  }
}

output "dataset_self_links" {
  description = "Map of dataset names to self links"
  value = {
    for k, v in google_bigquery_dataset.datasets : k => v.self_link
  }
}
```

### modules/cloud-storage/main.tf

```hcl
resource "google_storage_bucket" "buckets" {
  for_each = var.buckets
  
  project  = var.project_id
  name     = each.value.name
  location = each.value.location
  
  storage_class = each.value.storage_class
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = each.value.versioning
  }
  
  dynamic "lifecycle_rule" {
    for_each = each.value.lifecycle_rules
    content {
      action {
        type = lifecycle_rule.value.action.type
      }
      condition {
        age = lifecycle_rule.value.condition.age
      }
    }
  }
  
  labels = var.labels
  
  force_destroy = var.environment == "dev" ? true : false
}

# Create folder structure in data bucket
resource "google_storage_bucket_object" "folders" {
  for_each = toset([
    "finops/raw/",
    "finops/processed/",
    "workload-metrics/raw/",
    "workload-metrics/processed/",
    "migration-logs/"
  ])
  
  bucket  = google_storage_bucket.buckets["data"].name
  name    = each.value
  content = " "
}
```

### modules/cloud-storage/variables.tf

```hcl
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default     = {}
}

variable "buckets" {
  description = "Cloud Storage buckets to create"
  type = map(object({
    name          = string
    location      = string
    storage_class = string
    versioning    = bool
    lifecycle_rules = list(object({
      action = object({
        type = string
      })
      condition = object({
        age = number
      })
    }))
  }))
}
```

### modules/cloud-storage/outputs.tf

```hcl
output "bucket_names" {
  description = "Map of bucket keys to names"
  value = {
    for k, v in google_storage_bucket.buckets : k => v.name
  }
}

output "bucket_urls" {
  description = "Map of bucket keys to URLs"
  value = {
    for k, v in google_storage_bucket.buckets : k => v.url
  }
}
```

### modules/cloud-run/main.tf

```hcl
resource "google_cloud_run_v2_service" "services" {
  for_each = var.services
  
  project  = var.project_id
  location = var.region
  name     = "${var.environment}-${each.value.name}"
  
  template {
    scaling {
      min_instance_count = each.value.scaling.min_instance_count
      max_instance_count = each.value.scaling.max_instance_count
    }
    
    containers {
      image = each.value.image
      
      resources {
        limits = each.value.resources.limits
      }
      
      dynamic "env" {
        for_each = each.value.env_vars
        content {
          name  = env.value.name
          value = env.value.value
        }
      }
    }
  }
  
  labels = var.labels
}

# Make services publicly accessible (for demo)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  for_each = var.services
  
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.services[each.key].name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

### modules/cloud-run/variables.tf

```hcl
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default     = {}
}

variable "services" {
  description = "Cloud Run services to create"
  type = map(object({
    name  = string
    image = string
    resources = object({
      limits = map(string)
    })
    scaling = object({
      min_instance_count = number
      max_instance_count = number
    })
    env_vars = list(object({
      name  = string
      value = string
    }))
  }))
}
```

### modules/cloud-run/outputs.tf

```hcl
output "service_urls" {
  description = "Map of service names to URLs"
  value = {
    for k, v in google_cloud_run_v2_service.services : k => v.uri
  }
}

output "service_names" {
  description = "Map of service keys to names"
  value = {
    for k, v in google_cloud_run_v2_service.services : k => v.name
  }
}
```

## Setup Scripts

### scripts/inventory_gcp_resources.py

```python
#!/usr/bin/env python3
"""
Inventory existing GCP resources before Terraform deployment.
"""

import json
import subprocess
from typing import Dict, List

def run_gcloud_command(command: List[str]) -> Dict:
    """Run gcloud command and return JSON output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout) if result.stdout else {}
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return {}

def inventory_resources(project_id: str) -> Dict:
    """Inventory all resources in the project."""
    
    inventory = {
        "project_id": project_id,
        "resources": {}
    }
    
    # BigQuery datasets
    print("Inventorying BigQuery datasets...")
    datasets = run_gcloud_command([
        "bq", "ls", "--format=json", f"--project_id={project_id}"
    ])
    inventory["resources"]["bigquery_datasets"] = datasets
    
    # Cloud Storage buckets
    print("Inventorying Cloud Storage buckets...")
    buckets = run_gcloud_command([
        "gcloud", "storage", "buckets", "list",
        f"--project={project_id}",
        "--format=json"
    ])
    inventory["resources"]["storage_buckets"] = buckets
    
    # Cloud Run services
    print("Inventorying Cloud Run services...")
    services = run_gcloud_command([
        "gcloud", "run", "services", "list",
        f"--project={project_id}",
        "--region=us-central1",
        "--format=json"
    ])
    inventory["resources"]["cloud_run_services"] = services
    
    # Enabled APIs
    print("Inventorying enabled APIs...")
    apis = run_gcloud_command([
        "gcloud", "services", "list",
        f"--project={project_id}",
        "--enabled",
        "--format=json"
    ])
    inventory["resources"]["enabled_apis"] = apis
    
    return inventory

if __name__ == "__main__":
    project_id = "ccibt-hack25ww7-730"
    inventory = inventory_resources(project_id)
    print(json.dumps(inventory, indent=2))
```

### scripts/setup_state_bucket.sh

```bash
#!/bin/bash
# Setup Terraform state bucket

PROJECT_ID="ccibt-hack25ww7-730"
BUCKET_NAME="${PROJECT_ID}-terraform-state"
REGION="us-central1"

echo "Creating Terraform state bucket..."

# Create bucket
gcloud storage buckets create "gs://${BUCKET_NAME}" \
  --project="${PROJECT_ID}" \
  --location="${REGION}" \
  --uniform-bucket-level-access

# Enable versioning
gcloud storage buckets update "gs://${BUCKET_NAME}" \
  --versioning

echo "Terraform state bucket created: gs://${BUCKET_NAME}"
```

## Implementation Steps

1. **Create State Bucket**
   ```bash
   cd terraform/scripts
   chmod +x setup_state_bucket.sh
   ./setup_state_bucket.sh
   ```

2. **Inventory Existing Resources**
   ```bash
   python scripts/inventory_gcp_resources.py > existing-resources.json
   ```

3. **Create Directory Structure**
   ```bash
   # Create all directories
   mkdir -p terraform/environments/{dev,prod}
   mkdir -p terraform/modules/{bigquery,cloud-storage,cloud-run,vertex-ai,monitoring,networking}
   mkdir -p terraform/scripts
   ```

4. **Create Configuration Files**
   - Copy the configurations above into their respective files
   - Adjust values as needed for your environment

5. **Initialize and Apply**
   ```bash
   cd terraform/environments/dev
   terraform init
   terraform plan
   terraform apply
   ```

## Next Steps

After Terraform setup is complete:
1. Switch to Code mode to implement the actual infrastructure
2. Test each module independently
3. Deploy to dev environment first
4. Validate all resources are created correctly
5. Document any manual steps required
6. Create prod environment configuration

---

**Note**: This is a planning document. Actual Terraform files should be created in Code mode.