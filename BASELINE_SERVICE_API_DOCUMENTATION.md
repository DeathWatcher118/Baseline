# Baseline Service API Documentation

## Connection Information

### Service Endpoints

#### Primary Endpoint (Cloud Function)
```
URL: https://us-central1-ccibt-hack25ww7-730.cloudfunctions.net/baseline-calculator
Method: POST
Content-Type: application/json
Authentication: None (Public)
```

#### Alternative Endpoint (Cloud Run)
```
URL: https://baseline-calculator-jgscwa2bzq-uc.a.run.app
Method: POST
Content-Type: application/json
Authentication: None (Public)
```

#### Management Console
```
URL: https://console.cloud.google.com/functions/details/us-central1/baseline-calculator?project=ccibt-hack25ww7-730
```

### GCP Project Details

| Property | Value |
|----------|-------|
| Project ID | `ccibt-hack25ww7-730` |
| Project Number | `322435744920` |
| Region | `us-central1` |
| Service Account | `322435744920-compute@developer.gserviceaccount.com` |

### BigQuery Connection

#### Source Data
```
Project: ccibt-hack25ww7-730
Dataset: hackaton
Table: cloud_workload_dataset
Location: us-central1
Full Path: ccibt-hack25ww7-730.hackaton.cloud_workload_dataset
```

#### Baseline Storage
```
Project: ccibt-hack25ww7-730
Dataset: hackaton
Table: Baseline
Location: us-central1
Full Path: ccibt-hack25ww7-730.hackaton.Baseline
```

---

## API Inputs

### HTTP Request Format

#### Method
```
POST
```

#### Headers
```http
Content-Type: application/json
```

#### Request Body Schema

```json
{
  "metric_name": "string (required)",
  "metric_column": "string (required)",
  "source_table": "string (required)",
  "lookback_days": "integer (optional, default: 30)",
  "calculation_method": "string (optional, default: 'simple_stats')"
}
```

### Input Parameters

#### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `metric_name` | string | Identifier for the baseline metric | Non-empty string |
| `metric_column` | string | Exact BigQuery column name to analyze | Must exist in source table |
| `source_table` | string | BigQuery table name (in hackaton dataset) | Must exist in dataset |

#### Optional Parameters

| Parameter | Type | Default | Description | Valid Values |
|-----------|------|---------|-------------|--------------|
| `lookback_days` | integer | 30 | Number of days of historical data | Positive integer |
| `calculation_method` | string | "simple_stats" | Statistical calculation method | "simple_stats", "rolling_average", "seasonal_decomposition" |

### Valid Column Names

Based on `cloud_workload_dataset` table schema:

| Metric Type | Column Name | Data Type |
|-------------|-------------|-----------|
| Error Rate | `Error_Rate _percentage_` | FLOAT |
| CPU Utilization | `CPU_Utilization_percentage_` | FLOAT |
| Memory Consumption | `Memory_Consumption_MB_` | INTEGER |
| Execution Time | `Task_Execution_Time _ms_` | INTEGER |
| System Throughput | `System_Throughput _tasks_sec_` | FLOAT |
| Task Waiting Time | `Task_Waiting_Time _ms_` | INTEGER |
| Network Bandwidth | `Network_Bandwidth_Utilization_Mbps_` | FLOAT |
| Active Users | `Number_of_Active_Users` | INTEGER |

### Example Requests

#### Minimal Request
```json
{
  "metric_name": "error_rate",
  "metric_column": "Error_Rate _percentage_",
  "source_table": "cloud_workload_dataset"
}
```

#### Complete Request
```json
{
  "metric_name": "cpu_utilization",
  "metric_column": "CPU_Utilization_percentage_",
  "source_table": "cloud_workload_dataset",
  "lookback_days": 30,
  "calculation_method": "simple_stats"
}
```

#### cURL Examples

**Error Rate Baseline:**
```bash
curl -X POST \
  https://us-central1-ccibt-hack25ww7-730.cloudfunctions.net/baseline-calculator \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "error_rate",
    "metric_column": "Error_Rate _percentage_",
    "source_table": "cloud_workload_dataset"
  }'
```

**CPU Utilization with Custom Lookback:**
```bash
curl -X POST \
  https://us-central1-ccibt-hack25ww7-730.cloudfunctions.net/baseline-calculator \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "cpu_utilization",
    "metric_column": "CPU_Utilization_percentage_",
    "source_table": "cloud_workload_dataset",
    "lookback_days": 60
  }'
```

**Python Example:**
```python
import requests
import json

url = "https://us-central1-ccibt-hack25ww7-730.cloudfunctions.net/baseline-calculator"
headers = {"Content-Type": "application/json"}
payload = {
    "metric_name": "memory_consumption",
    "metric_column": "Memory_Consumption_MB_",
    "source_table": "cloud_workload_dataset"
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.json())
```

**JavaScript Example:**
```javascript
const url = 'https://us-central1-ccibt-hack25ww7-730.cloudfunctions.net/baseline-calculator';
const payload = {
  metric_name: 'execution_time',
  metric_column: 'Task_Execution_Time _ms_',
  source_table: 'cloud_workload_dataset'
};

fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## API Outputs

### Success Response (HTTP 200)

#### Response Schema
```json
{
  "success": true,
  "baseline_id": "string",
  "metric_name": "string",
  "mean": "float",
  "std_dev": "float",
  "min_value": "float",
  "max_value": "float",
  "p50": "float",
  "p95": "float",
  "p99": "float",
  "sample_count": "integer",
  "calculation_method": "string",
  "lookback_days": "integer",
  "calculated_at": "string (ISO 8601 timestamp)"
}
```

#### Response Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `success` | boolean | Indicates successful calculation | `true` |
| `baseline_id` | string | Unique identifier for this baseline | `"baseline-error_rate-20251216-210843"` |
| `metric_name` | string | Name of the metric analyzed | `"error_rate"` |
| `mean` | float | Average value of the metric | `2.52` |
| `std_dev` | float | Standard deviation | `1.45` |
| `min_value` | float | Minimum value observed | `0.0` |
| `max_value` | float | Maximum value observed | `5.0` |
| `p50` | float | Median (50th percentile) | `2.52` |
| `p95` | float | 95th percentile | `4.77` |
| `p99` | float | 99th percentile | `4.96` |
| `sample_count` | integer | Number of data points analyzed | `5000` |
| `calculation_method` | string | Method used for calculation | `"simple_stats"` |
| `lookback_days` | integer | Days of data analyzed | `30` |
| `calculated_at` | string | Timestamp of calculation (UTC) | `"2025-12-16T21:08:43Z"` |

#### Example Success Response
```json
{
  "success": true,
  "baseline_id": "baseline-error_rate-20251216-210843",
  "metric_name": "error_rate",
  "mean": 2.5219320000000027,
  "std_dev": 1.4532168300728696,
  "min_value": 0.0,
  "max_value": 5.0,
  "p50": 2.52,
  "p95": 4.77,
  "p99": 4.96,
  "sample_count": 5000,
  "calculation_method": "simple_stats",
  "lookback_days": 30,
  "calculated_at": "2025-12-16T21:08:43.129204Z"
}
```

### Error Responses

#### Missing Required Fields (HTTP 400)
```json
{
  "error": "Missing required fields",
  "missing": ["metric_column"],
  "required": ["metric_name", "metric_column", "source_table"]
}
```

#### Invalid Request Body (HTTP 400)
```json
{
  "error": "Invalid request",
  "message": "Request body must be JSON"
}
```

#### Validation Error (HTTP 400)
```json
{
  "error": "Validation error",
  "message": "No data found for metric error_rate"
}
```

#### Internal Server Error (HTTP 500)
```json
{
  "error": "Internal server error",
  "message": "Unrecognized name: `Invalid_Column` at [12:15]",
  "type": "BadRequest"
}
```

### BigQuery Output

In addition to the HTTP response, the baseline is automatically saved to BigQuery:

#### Table: `ccibt-hack25ww7-730.hackaton.Baseline`

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| baseline_id | STRING | REQUIRED | Unique identifier |
| metric_name | STRING | REQUIRED | Metric name |
| mean | FLOAT | REQUIRED | Average value |
| std_dev | FLOAT | REQUIRED | Standard deviation |
| min_value | FLOAT | REQUIRED | Minimum value |
| max_value | FLOAT | REQUIRED | Maximum value |
| p50 | FLOAT | REQUIRED | 50th percentile |
| p95 | FLOAT | REQUIRED | 95th percentile |
| p99 | FLOAT | REQUIRED | 99th percentile |
| calculated_at | TIMESTAMP | REQUIRED | Calculation timestamp |
| lookback_days | INTEGER | REQUIRED | Days analyzed |
| sample_count | INTEGER | REQUIRED | Number of samples |
| data_source | STRING | REQUIRED | Source table name |
| notes | STRING | NULLABLE | Additional notes |

#### Query Saved Baselines
```sql
-- Get latest baseline for a metric
SELECT *
FROM `ccibt-hack25ww7-730.hackaton.Baseline`
WHERE metric_name = 'error_rate'
ORDER BY calculated_at DESC
LIMIT 1;

-- Get all baselines for today
SELECT *
FROM `ccibt-hack25ww7-730.hackaton.Baseline`
WHERE DATE(calculated_at) = CURRENT_DATE()
ORDER BY calculated_at DESC;

-- Compare baselines over time
SELECT 
  metric_name,
  DATE(calculated_at) as date,
  mean,
  std_dev,
  p95,
  p99
FROM `ccibt-hack25ww7-730.hackaton.Baseline`
WHERE metric_name IN ('error_rate', 'cpu_utilization')
ORDER BY metric_name, calculated_at DESC;
```

---

## Connection Flow

```
┌─────────────┐
│   Client    │
│ Application │
└──────┬──────┘
       │ HTTP POST
       │ JSON Payload
       ▼
┌─────────────────────────────────────┐
│  Cloud Function: baseline-calculator│
│  Region: us-central1                │
│  Runtime: Python 3.14               │
└──────┬──────────────────────┬───────┘
       │                      │
       │ Query Data           │ Save Results
       ▼                      ▼
┌──────────────────┐   ┌──────────────────┐
│    BigQuery      │   │    BigQuery      │
│ cloud_workload_  │   │    Baseline      │
│    dataset       │   │     Table        │
│  (Source Data)   │   │  (Output Data)   │
└──────────────────┘   └──────────────────┘
```

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Cold Start Time | 2-3 seconds |
| Warm Request Time | 1-2 seconds |
| Average Calculation Time | ~1 second per metric |
| BigQuery Query Time | ~500ms |
| BigQuery Save Time | ~200ms |
| Timeout | 540 seconds (9 minutes) |
| Max Concurrent Requests | 100 instances |
| Request Concurrency | 1 per instance |

---

## Rate Limits & Quotas

### Cloud Functions Quotas
- **Invocations per day:** 2,000,000 (default)
- **Concurrent executions:** 100 (configured)
- **Memory:** 1 GiB per instance
- **Timeout:** 540 seconds per request

### BigQuery Quotas
- **Query rate:** 100 concurrent queries
- **Streaming inserts:** 100,000 rows per second per table
- **Storage:** Unlimited (pay per GB)

---

## Monitoring & Logging

### Cloud Logging
```
Log Name: projects/ccibt-hack25ww7-730/logs/cloudfunctions.googleapis.com%2Fcloud-functions
Filter: resource.labels.function_name="baseline-calculator"
```

### View Logs (gcloud)
```bash
gcloud functions logs read baseline-calculator \
  --region=us-central1 \
  --project=ccibt-hack25ww7-730 \
  --limit=50
```

### Metrics Available
- Request count
- Execution time
- Error rate
- Memory usage
- CPU utilization
- Active instances

---

## Security & Authentication

### Current Configuration
- **Authentication:** None (Public endpoint)
- **CORS:** Enabled (Allow all origins)
- **Service Account:** Automatic (GCP managed)

### Recommended for Production
```bash
# Deploy with authentication required
gcloud functions deploy baseline-calculator \
  --no-allow-unauthenticated \
  --region=us-central1 \
  --project=ccibt-hack25ww7-730

# Call with authentication
curl -X POST \
  https://us-central1-ccibt-hack25ww7-730.cloudfunctions.net/baseline-calculator \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{"metric_name": "error_rate", ...}'
```

---

## Troubleshooting

### Common Issues

#### 1. Column Not Found Error
```json
{
  "error": "Internal server error",
  "message": "Unrecognized name: `Error_Rate _%_`"
}
```
**Solution:** Use exact column name with correct spacing: `Error_Rate _percentage_`

#### 2. No Data Found
```json
{
  "error": "Validation error",
  "message": "No data found for metric error_rate"
}
```
**Solution:** Verify source table has data and column name is correct

#### 3. Timeout Error
**Solution:** Reduce lookback_days or optimize query

#### 4. Authentication Error (if enabled)
**Solution:** Include valid Bearer token in Authorization header

---

## Support & Contact

- **GCP Console:** https://console.cloud.google.com/functions/details/us-central1/baseline-calculator?project=ccibt-hack25ww7-730
- **Project:** ccibt-hack25ww7-730
- **Region:** us-central1
- **Service:** baseline-calculator

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-16 | Initial deployment with simple_stats method |
| 1.0.1 | 2025-12-16 | Fixed .env authentication issue |
| 1.0.2 | 2025-12-16 | Added baseline saving to BigQuery |

---

**Last Updated:** 2025-12-16  
**Status:** Production Ready ✅