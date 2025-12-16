# Data Sources Documentation

## Existing Dataset

### Primary Dataset Location

**BigQuery Dataset**: `datasets-ccibt-hack25ww7-730/datasets/uc3-volume-spikes-analyzer`

**Project**: ccibt-hack25ww7-730  
**Location**: US (multi-region)  
**Purpose**: Volume spikes analysis for hackathon challenge

---

## Dataset Exploration

### Step 1: Access the Dataset

```bash
# Set project
gcloud config set project ccibt-hack25ww7-730

# List tables in the dataset
bq ls datasets-ccibt-hack25ww7-730:uc3-volume-spikes-analyzer

# Or using full path
bq ls --project_id=datasets-ccibt-hack25ww7-730 uc3-volume-spikes-analyzer
```

### Step 2: Explore Table Schemas

```bash
# Get schema for each table
bq show --schema --format=prettyjson \
  datasets-ccibt-hack25ww7-730:uc3-volume-spikes-analyzer.TABLE_NAME

# Get table info
bq show datasets-ccibt-hack25ww7-730:uc3-volume-spikes-analyzer.TABLE_NAME
```

### Step 3: Sample Data Queries

```sql
-- List all tables and row counts
SELECT 
  table_name,
  row_count,
  size_bytes / 1024 / 1024 as size_mb
FROM 
  `datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer.__TABLES__`
ORDER BY 
  row_count DESC;

-- Sample data from a table (replace TABLE_NAME)
SELECT *
FROM `datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer.TABLE_NAME`
LIMIT 10;

-- Get date range of data
SELECT 
  MIN(timestamp_column) as earliest_date,
  MAX(timestamp_column) as latest_date,
  COUNT(*) as total_records
FROM `datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer.TABLE_NAME`;
```

---

## Python Data Access

### Using BigQuery Client

```python
from google.cloud import bigquery
import pandas as pd

# Initialize client
client = bigquery.Client(project='ccibt-hack25ww7-730')

# List tables in dataset
dataset_id = 'datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer'
tables = client.list_tables(dataset_id)

print("Tables in dataset:")
for table in tables:
    print(f"  - {table.table_id}")

# Query data
query = """
SELECT *
FROM `datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer.TABLE_NAME`
LIMIT 1000
"""

df = client.query(query).to_dataframe()
print(f"Loaded {len(df)} rows")
print(df.head())
```

### Explore Schema Programmatically

```python
from google.cloud import bigquery

client = bigquery.Client(project='ccibt-hack25ww7-730')

# Get table reference
table_ref = client.dataset(
    'uc3-volume-spikes-analyzer',
    project='datasets-ccibt-hack25ww7-730'
).table('TABLE_NAME')

# Get table
table = client.get_table(table_ref)

# Print schema
print(f"Table: {table.table_id}")
print(f"Rows: {table.num_rows}")
print(f"Size: {table.num_bytes / 1024 / 1024:.2f} MB")
print("\nSchema:")
for field in table.schema:
    print(f"  - {field.name}: {field.field_type} ({field.mode})")
```

---

## Expected Data Structure

Based on the challenge requirements, the dataset likely contains:

### FinOps/Cost Data
```sql
-- Expected columns
timestamp TIMESTAMP
resource_id STRING
resource_type STRING
cost FLOAT64
usage_amount FLOAT64
usage_unit STRING
project_id STRING
region STRING
labels JSON
```

### Workload Metrics
```sql
-- Expected columns
timestamp TIMESTAMP
workload_id STRING
workload_name STRING
metric_type STRING  -- cpu, memory, requests, etc.
metric_value FLOAT64
resource_id STRING
namespace STRING
labels JSON
```

### Migration/Event Logs
```sql
-- Expected columns
timestamp TIMESTAMP
event_id STRING
event_type STRING  -- migration, deployment, config_change
source_location STRING
target_location STRING
resources_affected INT64
status STRING
details JSON
```

---

## Data Exploration Script

Create `scripts/explore_dataset.py`:

```python
#!/usr/bin/env python3
"""
Explore the existing BigQuery dataset
"""

from google.cloud import bigquery
import pandas as pd
from datetime import datetime

def explore_dataset():
    """Explore the uc3-volume-spikes-analyzer dataset"""
    
    client = bigquery.Client(project='ccibt-hack25ww7-730')
    dataset_id = 'datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer'
    
    print("=" * 80)
    print("Exploring Dataset: uc3-volume-spikes-analyzer")
    print("=" * 80)
    
    # List all tables
    print("\n1. Tables in Dataset:")
    print("-" * 80)
    tables = list(client.list_tables(dataset_id))
    
    if not tables:
        print("No tables found in dataset")
        return
    
    for table in tables:
        table_ref = client.dataset(
            'uc3-volume-spikes-analyzer',
            project='datasets-ccibt-hack25ww7-730'
        ).table(table.table_id)
        
        table_obj = client.get_table(table_ref)
        
        print(f"\nTable: {table.table_id}")
        print(f"  Rows: {table_obj.num_rows:,}")
        print(f"  Size: {table_obj.num_bytes / 1024 / 1024:.2f} MB")
        print(f"  Created: {table_obj.created}")
        print(f"  Modified: {table_obj.modified}")
        
        # Print schema
        print(f"  Schema:")
        for field in table_obj.schema:
            print(f"    - {field.name}: {field.field_type} ({field.mode})")
        
        # Sample data
        query = f"""
        SELECT *
        FROM `{dataset_id}.{table.table_id}`
        LIMIT 5
        """
        
        try:
            df = client.query(query).to_dataframe()
            print(f"\n  Sample Data:")
            print(df.to_string(index=False))
        except Exception as e:
            print(f"  Error sampling data: {e}")
        
        print("\n" + "-" * 80)
    
    # Summary statistics
    print("\n2. Dataset Summary:")
    print("-" * 80)
    
    for table in tables:
        query = f"""
        SELECT 
            '{table.table_id}' as table_name,
            COUNT(*) as row_count,
            COUNT(DISTINCT DATE(timestamp)) as unique_dates
        FROM `{dataset_id}.{table.table_id}`
        """
        
        try:
            result = client.query(query).to_dataframe()
            print(f"\n{table.table_id}:")
            print(f"  Total Rows: {result['row_count'].iloc[0]:,}")
            print(f"  Unique Dates: {result['unique_dates'].iloc[0]:,}")
        except Exception as e:
            print(f"  Error getting summary: {e}")

if __name__ == "__main__":
    explore_dataset()
```

Run the script:
```bash
python scripts/explore_dataset.py
```

---

## Data Access Patterns

### For Anomaly Detection

```python
def get_metric_data(metric_type, start_date, end_date):
    """Get metric data for anomaly detection"""
    
    query = f"""
    SELECT 
        timestamp,
        metric_value,
        resource_id,
        labels
    FROM `datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer.metrics`
    WHERE 
        metric_type = @metric_type
        AND timestamp BETWEEN @start_date AND @end_date
    ORDER BY timestamp
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("metric_type", "STRING", metric_type),
            bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date),
            bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date),
        ]
    )
    
    return client.query(query, job_config=job_config).to_dataframe()
```

### For Correlation Analysis

```python
def get_events_in_timewindow(center_time, window_minutes=60):
    """Get events within time window for correlation"""
    
    query = f"""
    SELECT 
        timestamp,
        event_type,
        event_id,
        details
    FROM `datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer.events`
    WHERE 
        timestamp BETWEEN 
            TIMESTAMP_SUB(@center_time, INTERVAL @window_minutes MINUTE)
            AND TIMESTAMP_ADD(@center_time, INTERVAL @window_minutes MINUTE)
    ORDER BY timestamp
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("center_time", "TIMESTAMP", center_time),
            bigquery.ScalarQueryParameter("window_minutes", "INT64", window_minutes),
        ]
    )
    
    return client.query(query, job_config=job_config).to_dataframe()
```

---

## Data Quality Checks

```python
def check_data_quality():
    """Run data quality checks"""
    
    checks = {
        "null_timestamps": """
            SELECT COUNT(*) as null_count
            FROM `datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer.TABLE_NAME`
            WHERE timestamp IS NULL
        """,
        
        "duplicate_records": """
            SELECT 
                timestamp,
                resource_id,
                COUNT(*) as duplicate_count
            FROM `datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer.TABLE_NAME`
            GROUP BY timestamp, resource_id
            HAVING COUNT(*) > 1
        """,
        
        "date_range": """
            SELECT 
                MIN(timestamp) as earliest,
                MAX(timestamp) as latest,
                TIMESTAMP_DIFF(MAX(timestamp), MIN(timestamp), DAY) as days_span
            FROM `datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer.TABLE_NAME`
        """
    }
    
    for check_name, query in checks.items():
        print(f"\n{check_name}:")
        result = client.query(query).to_dataframe()
        print(result)
```

---

## Integration with Application

### Update Configuration

Add to `.env`:
```bash
# Existing Dataset
BIGQUERY_SOURCE_PROJECT=datasets-ccibt-hack25ww7-730
BIGQUERY_SOURCE_DATASET=uc3-volume-spikes-analyzer

# Working Dataset (your project)
BIGQUERY_WORKING_PROJECT=ccibt-hack25ww7-730
BIGQUERY_WORKING_DATASET=anomaly_results
```

### Update Data Access Layer

```python
# src/data/storage/bigquery.py

import os
from google.cloud import bigquery

class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client(project='ccibt-hack25ww7-730')
        self.source_project = os.getenv('BIGQUERY_SOURCE_PROJECT')
        self.source_dataset = os.getenv('BIGQUERY_SOURCE_DATASET')
    
    def get_source_table(self, table_name):
        """Get fully qualified source table name"""
        return f"{self.source_project}.{self.source_dataset}.{table_name}"
    
    def query_source_data(self, query):
        """Query data from source dataset"""
        return self.client.query(query).to_dataframe()
```

---

## Next Steps

1. **Explore the Dataset**
   ```bash
   python scripts/explore_dataset.py
   ```

2. **Document Findings**
   - Update this document with actual table names
   - Document schema details
   - Note data quality issues
   - Identify key metrics for analysis

3. **Create Sample Queries**
   - Queries for anomaly detection
   - Queries for correlation analysis
   - Queries for reporting

4. **Update Implementation**
   - Modify detection logic to use actual schema
   - Update API to query real data
   - Adjust agent tools for actual tables

---

## Quick Reference

### Access Dataset
```bash
# Via bq command
bq ls datasets-ccibt-hack25ww7-730:uc3-volume-spikes-analyzer

# Via Python
from google.cloud import bigquery
client = bigquery.Client(project='ccibt-hack25ww7-730')
tables = client.list_tables('datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer')
```

### Query Data
```sql
SELECT *
FROM `datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer.TABLE_NAME`
LIMIT 10;
```

### Grant Access (if needed)
```bash
# Grant your service account access
bq add-iam-policy-binding \
  --member="serviceAccount:YOUR-SA@ccibt-hack25ww7-730.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer" \
  datasets-ccibt-hack25ww7-730:uc3-volume-spikes-analyzer
```

---

**Document Version**: 1.0  
**Last Updated**: 2024-12-16  
**Dataset**: datasets-ccibt-hack25ww7-730/uc3-volume-spikes-analyzer