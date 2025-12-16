# Terraform Infrastructure

This directory contains Terraform configurations for managing GCP infrastructure for the Anomaly Detection System.

## Directory Structure

```
terraform/
├── environments/
│   ├── dev/          # Development environment
│   └── prod/         # Production environment
├── modules/          # Reusable Terraform modules
│   ├── bigquery/
│   ├── cloud-storage/
│   ├── cloud-run/
│   ├── vertex-ai/
│   ├── monitoring/
│   └── networking/
└── README.md
```

## Prerequisites

1. **Terraform Installation**
   ```bash
   # Install Terraform >= 1.5.0
   # Windows (using Chocolatey)
   choco install terraform
   
   # Verify installation
   terraform version
   ```

2. **GCP Authentication**
   ```bash
   # Authenticate with GCP
   gcloud auth application-default login
   
   # Set project
   gcloud config set project ccibt-hack25ww7-730
   ```

3. **Enable Required APIs**
   ```bash
   # Enable all required GCP APIs
   gcloud services enable \
     compute.googleapis.com \
     storage.googleapis.com \
     bigquery.googleapis.com \
     aiplatform.googleapis.com \
     run.googleapis.com \
     cloudfunctions.googleapis.com \
     pubsub.googleapis.com \
     monitoring.googleapis.com \
     logging.googleapis.com \
     cloudresourcemanager.googleapis.com \
     iam.googleapis.com \
     secretmanager.googleapis.com
   ```

## Initial Setup

### 1. Create Terraform State Bucket

Before running Terraform, create a GCS bucket for storing Terraform state:

```bash
# Create state bucket
gcloud storage buckets create gs://ccibt-hack25ww7-730-terraform-state \
  --project=ccibt-hack25ww7-730 \
  --location=us-central1 \
  --uniform-bucket-level-access

# Enable versioning
gcloud storage buckets update gs://ccibt-hack25ww7-730-terraform-state \
  --versioning
```

### 2. Inventory Existing Resources

Before creating new infrastructure, inventory existing GCP resources:

```bash
# Run inventory script
cd terraform
python scripts/inventory_gcp_resources.py > existing-resources.json

# Review existing resources
cat existing-resources.json
```

### 3. Initialize Terraform

```bash
# Navigate to environment directory
cd terraform/environments/dev

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive
```

## Usage

### Development Environment

```bash
cd terraform/environments/dev

# Plan changes
terraform plan -out=tfplan

# Review plan
terraform show tfplan

# Apply changes
terraform apply tfplan

# View outputs
terraform output
```

### Production Environment

```bash
cd terraform/environments/prod

# Plan changes
terraform plan -out=tfplan

# Review plan (IMPORTANT: Review carefully!)
terraform show tfplan

# Apply changes (requires approval)
terraform apply tfplan
```

## Common Commands

```bash
# Initialize/update providers
terraform init -upgrade

# Plan changes
terraform plan

# Apply changes
terraform apply

# Destroy resources (DANGEROUS!)
terraform destroy

# Show current state
terraform show

# List resources
terraform state list

# Import existing resource
terraform import <resource_type>.<name> <resource_id>

# Format code
terraform fmt -recursive

# Validate configuration
terraform validate

# View outputs
terraform output

# Refresh state
terraform refresh
```

## Module Usage

### BigQuery Module

```hcl
module "bigquery" {
  source = "../../modules/bigquery"
  
  project_id = var.project_id
  region     = var.region
  
  datasets = {
    finops_data = {
      description = "FinOps cost and usage data"
      location    = "US"
    }
    workload_metrics = {
      description = "Workload performance metrics"
      location    = "US"
    }
  }
}
```

### Cloud Storage Module

```hcl
module "storage" {
  source = "../../modules/cloud-storage"
  
  project_id = var.project_id
  region     = var.region
  
  buckets = {
    data = {
      name     = "ccibt-hack25ww7-730-data"
      location = "US"
      lifecycle_rules = [
        {
          action    = "Delete"
          condition = { age = 90 }
        }
      ]
    }
  }
}
```

### Cloud Run Module

```hcl
module "cloud_run" {
  source = "../../modules/cloud-run"
  
  project_id = var.project_id
  region     = var.region
  
  services = {
    api = {
      name  = "anomaly-detection-api"
      image = "gcr.io/ccibt-hack25ww7-730/api:latest"
      
      resources = {
        cpu    = "2"
        memory = "4Gi"
      }
      
      scaling = {
        min_instances = 1
        max_instances = 10
      }
    }
  }
}
```

## Best Practices

### 1. State Management

- **Never** commit `terraform.tfstate` to Git
- Always use remote state (GCS backend)
- Enable state locking
- Use separate state files per environment

### 2. Variable Management

- Use `terraform.tfvars` for environment-specific values
- Never commit sensitive values to Git
- Use Secret Manager for secrets
- Document all variables in `variables.tf`

### 3. Resource Naming

Follow the naming convention:
```
{project}-{environment}-{resource-type}-{name}

Examples:
- ccibt-hack25ww7-730-dev-bucket-data
- ccibt-hack25ww7-730-prod-dataset-finops
- ccibt-hack25ww7-730-dev-service-api
```

### 4. Tagging/Labeling

Always include these labels:
```hcl
labels = {
  environment = var.environment
  project     = "hackathon-anomaly-detection"
  managed_by  = "terraform"
  cost_center = "hackathon"
}
```

### 5. Change Management

1. Always run `terraform plan` first
2. Review the plan carefully
3. Apply changes during maintenance windows
4. Document changes in Git commit messages
5. Test in dev before applying to prod

### 6. Security

- Use service accounts with minimal permissions
- Enable audit logging
- Encrypt sensitive data
- Use Private Google Access
- Implement network security rules

## Troubleshooting

### State Lock Issues

```bash
# If state is locked
terraform force-unlock <LOCK_ID>

# Only use if you're sure no other process is running
```

### Import Existing Resources

```bash
# Example: Import existing BigQuery dataset
terraform import module.bigquery.google_bigquery_dataset.dataset \
  projects/ccibt-hack25ww7-730/datasets/existing_dataset

# Example: Import existing Cloud Storage bucket
terraform import module.storage.google_storage_bucket.bucket \
  ccibt-hack25ww7-730-existing-bucket
```

### State Drift

```bash
# Detect drift
terraform plan -refresh-only

# Update state to match reality
terraform apply -refresh-only
```

### Provider Issues

```bash
# Clear provider cache
rm -rf .terraform

# Reinitialize
terraform init -upgrade
```

## Cost Estimation

Before applying changes, estimate costs:

```bash
# Using Terraform Cloud (if configured)
terraform plan

# Using Infracost (if installed)
infracost breakdown --path .
```

## Maintenance

### Regular Tasks

1. **Weekly**: Review and update provider versions
2. **Monthly**: Review resource usage and costs
3. **Quarterly**: Audit IAM permissions
4. **As needed**: Update module versions

### Cleanup

```bash
# Remove unused resources
terraform state list | grep unused | xargs -I {} terraform state rm {}

# Clean up old state versions (in GCS console)
# Keep last 10 versions, delete older ones
```

## Emergency Procedures

### Rollback

```bash
# List state versions
gsutil ls -l gs://ccibt-hack25ww7-730-terraform-state/terraform/state/

# Download previous version
gsutil cp gs://ccibt-hack25ww7-730-terraform-state/terraform/state/<version> \
  terraform.tfstate

# Apply previous state
terraform apply
```

### Disaster Recovery

1. Restore state from backup
2. Run `terraform plan` to verify
3. Apply changes if needed
4. Verify all resources are healthy

## Additional Resources

- [Terraform GCP Provider Documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [GCP Best Practices](https://cloud.google.com/docs/terraform/best-practices-for-terraform)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)

## Support

For issues or questions:
1. Check this README
2. Review Terraform documentation
3. Check GCP documentation
4. Contact team lead

---

**Last Updated**: 2024-12-16  
**Maintained By**: Hackathon Team