# Anomaly Detector → AI Agent Interface Specification

## Overview

This document specifies the **exact data contract** between Anomaly Detection systems and the AI Agent for Anomaly Analysis. Any anomaly detector must provide this information for the AI Agent to perform its analysis.

## Required Data Structure

### Minimum Required Fields

The anomaly detector **MUST** provide these fields:

```python
{
    "anomaly_id": str,              # Unique identifier for this anomaly
    "detected_at": datetime/ISO8601, # When the anomaly was detected
    "metric_name": str,              # Name of the metric (e.g., "error_rate")
    "metric_type": str,              # Type classification (see below)
    "current_value": float,          # Current observed value
    "baseline_value": float,         # Expected baseline value
    "deviation_sigma": float,        # Standard deviations from baseline
    "deviation_percentage": float,   # Percentage deviation from baseline
    "anomaly_type": str,             # STABILITY, PERFORMANCE, COST, RESOURCE
    "severity": str,                 # CRITICAL, HIGH, MEDIUM, LOW, INFO
    "confidence": float              # Detection confidence (0.0-1.0)
}
```

### Optional But Highly Recommended Fields

These fields significantly improve analysis quality:

```python
{
    "affected_resources": [          # Resources impacted by anomaly
        {
            "resource_type": str,    # e.g., "job", "machine", "service"
            "resource_id": str,      # e.g., "JOB_1234", "MACH_890"
            "impact_level": str      # "high", "medium", "low"
        }
    ],
    "related_metrics": {             # Other metrics at detection time
        "cpu_usage": float,
        "memory_usage": float,
        "request_rate": float,
        # ... any relevant metrics
    },
    "time_window": {                 # Detection window
        "start": datetime/ISO8601,
        "end": datetime/ISO8601,
        "duration_seconds": int
    },
    "detection_method": str,         # e.g., "z-score", "percentile", "ml-model"
    "historical_context": {          # Historical comparison
        "previous_anomalies": int,   # Count in last 24h
        "trend": str,                # "increasing", "stable", "decreasing"
        "seasonality": str           # "daily", "weekly", "none"
    }
}
```

## Field Specifications

### 1. anomaly_id (REQUIRED)
- **Type**: String
- **Format**: Unique identifier (UUID recommended)
- **Example**: `"anom-2025-12-16-001"`, `"550e8400-e29b-41d4-a716-446655440000"`
- **Purpose**: Track and reference this specific anomaly

### 2. detected_at (REQUIRED)
- **Type**: Datetime or ISO 8601 string
- **Format**: `YYYY-MM-DDTHH:MM:SS.sssZ` (UTC preferred)
- **Example**: `"2025-12-16T16:30:45.123Z"`
- **Purpose**: Timestamp when anomaly was first detected

### 3. metric_name (REQUIRED)
- **Type**: String
- **Format**: Descriptive name of the metric
- **Examples**: 
  - `"error_rate"`
  - `"task_execution_time"`
  - `"cpu_utilization"`
  - `"memory_usage"`
  - `"request_latency"`
  - `"compute_cost"`
- **Purpose**: Identify what metric is anomalous

### 4. metric_type (REQUIRED)
- **Type**: String
- **Format**: Classification from your data schema
- **Valid Values**:
  - `"Error_Rate _%_"`
  - `"Task_Execution_Time _ms_"`
  - `"CPU_Utilization _%_"`
  - `"Memory_Usage _%_"`
  - `"Request_Rate _per_sec_"`
  - `"Cost_USD"`
  - `"Latency_ms"`
- **Purpose**: Helps AI understand metric characteristics and units

### 5. current_value (REQUIRED)
- **Type**: Float
- **Format**: Numeric value in metric's native units
- **Example**: `45.0` (for 45% error rate), `850.0` (for 850ms latency)
- **Purpose**: The actual observed value that triggered the anomaly

### 6. baseline_value (REQUIRED)
- **Type**: Float
- **Format**: Expected normal value for this metric
- **Example**: `22.8` (expected error rate), `320.0` (expected latency)
- **Purpose**: Reference point for understanding deviation magnitude
- **Note**: This comes from your baseline calculator

### 7. deviation_sigma (REQUIRED)
- **Type**: Float
- **Format**: Number of standard deviations from baseline
- **Example**: `5.3` (5.3 standard deviations above normal)
- **Purpose**: Statistical significance of the anomaly
- **Typical Ranges**:
  - `< 3.0`: Moderate anomaly
  - `3.0 - 5.0`: Significant anomaly
  - `> 5.0`: Extreme anomaly

### 8. deviation_percentage (REQUIRED)
- **Type**: Float
- **Format**: Percentage deviation from baseline
- **Example**: `97.4` (97.4% higher than baseline)
- **Calculation**: `((current_value - baseline_value) / baseline_value) * 100`
- **Purpose**: Human-readable magnitude of deviation

### 9. anomaly_type (REQUIRED)
- **Type**: String (Enum)
- **Valid Values**:
  - `"STABILITY"`: System reliability issues (errors, failures, crashes)
  - `"PERFORMANCE"`: Speed/efficiency issues (latency, throughput)
  - `"COST"`: Financial waste or unexpected spending
  - `"RESOURCE"`: Resource utilization issues (CPU, memory, disk)
  - `"UNKNOWN"`: Cannot be classified (AI will attempt to classify)
- **Purpose**: Determines recommendation strategy
- **Classification Guide**:
  ```
  Error rates, failure rates → STABILITY
  Latency, execution time, throughput → PERFORMANCE
  Compute cost, storage cost → COST
  CPU, memory, disk usage → RESOURCE
  ```

### 10. severity (REQUIRED)
- **Type**: String (Enum)
- **Valid Values**:
  - `"CRITICAL"`: Immediate action required, system at risk
  - `"HIGH"`: Urgent attention needed, significant impact
  - `"MEDIUM"`: Should be addressed soon, moderate impact
  - `"LOW"`: Monitor and address when convenient
  - `"INFO"`: Informational, no action needed
- **Purpose**: Prioritization and notification routing
- **Severity Guidelines**:
  ```
  CRITICAL: deviation_sigma > 5.0 OR critical resource affected
  HIGH: deviation_sigma > 3.0 OR high business impact
  MEDIUM: deviation_sigma > 2.0 OR moderate impact
  LOW: deviation_sigma > 1.5 OR low impact
  INFO: deviation_sigma <= 1.5
  ```

### 11. confidence (REQUIRED)
- **Type**: Float
- **Format**: Value between 0.0 and 1.0
- **Example**: `0.95` (95% confident this is a real anomaly)
- **Purpose**: Indicates detection reliability
- **Typical Ranges**:
  - `> 0.9`: High confidence, likely true anomaly
  - `0.7 - 0.9`: Moderate confidence, investigate
  - `< 0.7`: Low confidence, may be noise

### 12. affected_resources (OPTIONAL)
- **Type**: Array of objects
- **Format**:
  ```python
  [
      {
          "resource_type": "job",
          "resource_id": "JOB_1234",
          "impact_level": "high"
      },
      {
          "resource_type": "machine",
          "resource_id": "MACH_890",
          "impact_level": "medium"
      }
  ]
  ```
- **Purpose**: Identifies what's impacted, helps with root cause analysis

### 13. related_metrics (OPTIONAL)
- **Type**: Dictionary/Object
- **Format**: Key-value pairs of metric names and their values at detection time
- **Example**:
  ```python
  {
      "cpu_usage": 95.2,
      "memory_usage": 87.5,
      "request_rate": 1250.0,
      "active_connections": 450
  }
  ```
- **Purpose**: Provides context for correlation analysis

## Complete Example Payloads

### Example 1: Stability Anomaly (Error Rate Spike)

```json
{
    "anomaly_id": "anom-2025-12-16-001",
    "detected_at": "2025-12-16T16:30:45.123Z",
    "metric_name": "error_rate",
    "metric_type": "Error_Rate _%_",
    "current_value": 45.0,
    "baseline_value": 22.8,
    "deviation_sigma": 5.3,
    "deviation_percentage": 97.4,
    "anomaly_type": "STABILITY",
    "severity": "CRITICAL",
    "confidence": 0.95,
    "affected_resources": [
        {
            "resource_type": "job",
            "resource_id": "JOB_1234",
            "impact_level": "high"
        },
        {
            "resource_type": "machine",
            "resource_id": "MACH_890",
            "impact_level": "high"
        }
    ],
    "related_metrics": {
        "cpu_usage": 95.2,
        "memory_usage": 87.5,
        "request_rate": 1250.0,
        "task_failure_count": 45
    },
    "time_window": {
        "start": "2025-12-16T16:25:00Z",
        "end": "2025-12-16T16:30:00Z",
        "duration_seconds": 300
    },
    "detection_method": "z-score",
    "historical_context": {
        "previous_anomalies": 2,
        "trend": "increasing",
        "seasonality": "none"
    }
}
```

### Example 2: Performance Anomaly (Latency Increase)

```json
{
    "anomaly_id": "anom-2025-12-16-002",
    "detected_at": "2025-12-16T14:15:30.456Z",
    "metric_name": "task_execution_time",
    "metric_type": "Task_Execution_Time _ms_",
    "current_value": 850.0,
    "baseline_value": 320.0,
    "deviation_sigma": 4.2,
    "deviation_percentage": 165.6,
    "anomaly_type": "PERFORMANCE",
    "severity": "HIGH",
    "confidence": 0.88,
    "affected_resources": [
        {
            "resource_type": "service",
            "resource_id": "api-gateway",
            "impact_level": "high"
        }
    ],
    "related_metrics": {
        "cpu_usage": 78.5,
        "memory_usage": 65.2,
        "request_rate": 2100.0,
        "queue_depth": 350
    },
    "time_window": {
        "start": "2025-12-16T14:10:00Z",
        "end": "2025-12-16T14:15:00Z",
        "duration_seconds": 300
    },
    "detection_method": "percentile-based",
    "historical_context": {
        "previous_anomalies": 0,
        "trend": "stable",
        "seasonality": "daily"
    }
}
```

### Example 3: Cost Anomaly (Unexpected Spending)

```json
{
    "anomaly_id": "anom-2025-12-16-003",
    "detected_at": "2025-12-16T12:00:00.789Z",
    "metric_name": "compute_cost",
    "metric_type": "Cost_USD",
    "current_value": 1250.0,
    "baseline_value": 650.0,
    "deviation_sigma": 3.8,
    "deviation_percentage": 92.3,
    "anomaly_type": "COST",
    "severity": "MEDIUM",
    "confidence": 0.91,
    "affected_resources": [
        {
            "resource_type": "cluster",
            "resource_id": "prod-cluster-01",
            "impact_level": "medium"
        }
    ],
    "related_metrics": {
        "cpu_usage": 15.2,
        "memory_usage": 22.8,
        "instance_count": 50,
        "active_jobs": 12
    },
    "time_window": {
        "start": "2025-12-16T00:00:00Z",
        "end": "2025-12-16T12:00:00Z",
        "duration_seconds": 43200
    },
    "detection_method": "baseline-comparison",
    "historical_context": {
        "previous_anomalies": 1,
        "trend": "increasing",
        "seasonality": "weekly"
    }
}
```

## Integration Methods

### Method 1: Direct Function Call (Python)

```python
from src.agent.anomaly_analyzer import AnomalyAnalyzerAgent
from src.models.anomaly import Anomaly, AnomalyType, Severity
from datetime import datetime

# In your anomaly detector
def on_anomaly_detected(detection_data):
    # Create Anomaly object
    anomaly = Anomaly(
        anomaly_id=detection_data["anomaly_id"],
        detected_at=datetime.fromisoformat(detection_data["detected_at"]),
        metric_name=detection_data["metric_name"],
        metric_type=detection_data["metric_type"],
        current_value=detection_data["current_value"],
        baseline_value=detection_data["baseline_value"],
        deviation_sigma=detection_data["deviation_sigma"],
        deviation_percentage=detection_data["deviation_percentage"],
        anomaly_type=AnomalyType[detection_data["anomaly_type"]],
        severity=Severity[detection_data["severity"]],
        confidence=detection_data["confidence"],
        affected_resources=detection_data.get("affected_resources", []),
        related_metrics=detection_data.get("related_metrics", {})
    )
    
    # Analyze with AI Agent
    agent = AnomalyAnalyzerAgent()
    analysis = agent.analyze_anomaly(anomaly)
    
    # Analysis is automatically saved to BigQuery
    return analysis
```

### Method 2: REST API (Future Implementation)

```bash
POST /api/v1/analyze-anomaly
Content-Type: application/json

{
    "anomaly_id": "anom-2025-12-16-001",
    "detected_at": "2025-12-16T16:30:45.123Z",
    "metric_name": "error_rate",
    "metric_type": "Error_Rate _%_",
    "current_value": 45.0,
    "baseline_value": 22.8,
    "deviation_sigma": 5.3,
    "deviation_percentage": 97.4,
    "anomaly_type": "STABILITY",
    "severity": "CRITICAL",
    "confidence": 0.95
}
```

### Method 3: Pub/Sub Message (Event-Driven)

```python
from google.cloud import pubsub_v1
import json

# In your anomaly detector
def publish_anomaly(detection_data):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path('ccibt-hack25ww7-730', 'anomaly-detected')
    
    message_data = json.dumps(detection_data).encode('utf-8')
    future = publisher.publish(topic_path, message_data)
    
    return future.result()

# AI Agent subscribes to this topic and processes messages
```

### Method 4: BigQuery Table (Batch Processing)

```python
# Anomaly detector writes to BigQuery table
INSERT INTO `ccibt-hack25ww7-730.hackaton.DetectedAnomalies` (
    anomaly_id,
    detected_at,
    metric_name,
    current_value,
    baseline_value,
    deviation_sigma,
    anomaly_type,
    severity,
    confidence
) VALUES (
    'anom-2025-12-16-001',
    TIMESTAMP('2025-12-16T16:30:45.123Z'),
    'error_rate',
    45.0,
    22.8,
    5.3,
    'STABILITY',
    'CRITICAL',
    0.95
);

# AI Agent polls this table for unprocessed anomalies
```

## Validation Rules

The AI Agent will validate incoming data:

### Required Field Validation
```python
✓ All required fields must be present
✓ anomaly_id must be unique
✓ detected_at must be valid datetime
✓ current_value, baseline_value must be numeric
✓ deviation_sigma must be > 0
✓ confidence must be between 0.0 and 1.0
✓ anomaly_type must be valid enum value
✓ severity must be valid enum value
```

### Data Quality Checks
```python
⚠ Warning if confidence < 0.7 (low confidence)
⚠ Warning if deviation_sigma < 2.0 (may not be significant)
⚠ Warning if no affected_resources provided
⚠ Warning if no related_metrics provided
```

## Error Handling

### Invalid Data Response
```json
{
    "status": "error",
    "error_code": "INVALID_ANOMALY_DATA",
    "message": "Missing required field: baseline_value",
    "details": {
        "missing_fields": ["baseline_value"],
        "invalid_fields": []
    }
}
```

### Successful Analysis Response
```json
{
    "status": "success",
    "analysis_id": "analysis-550e8400-e29b-41d4-a716-446655440000",
    "anomaly_id": "anom-2025-12-16-001",
    "root_cause": {
        "primary_cause": "Elevated error rate due to resource contention",
        "confidence": 0.92
    },
    "recommendations_count": 3,
    "analyzed_at": "2025-12-16T16:30:50.456Z",
    "analysis_duration_ms": 1250
}
```

## Best Practices for Anomaly Detectors

1. **Always Provide Context**: Include affected_resources and related_metrics when possible
2. **Accurate Classification**: Set anomaly_type and severity appropriately
3. **Confidence Scores**: Be honest about detection confidence
4. **Unique IDs**: Use UUIDs or timestamp-based IDs for anomaly_id
5. **Timely Detection**: Send anomalies to AI Agent immediately upon detection
6. **Complete Data**: Provide all required fields to enable best analysis

## Summary

**Minimum Required Data (11 fields):**
1. anomaly_id
2. detected_at
3. metric_name
4. metric_type
5. current_value
6. baseline_value
7. deviation_sigma
8. deviation_percentage
9. anomaly_type
10. severity
11. confidence

**Recommended Additional Data:**
- affected_resources
- related_metrics
- time_window
- detection_method
- historical_context

**The more context you provide, the better the AI Agent's analysis and recommendations will be!**