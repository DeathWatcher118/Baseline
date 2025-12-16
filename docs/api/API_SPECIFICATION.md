# API Specification

REST API specification for the Anomaly Detection System.

## Base URL

- **Development**: `https://dev-anomaly-detection-api-<hash>-uc.a.run.app`
- **Production**: `https://anomaly-detection-api-<hash>-uc.a.run.app`

## Authentication

All API requests require authentication using API keys.

```http
Authorization: Bearer <api-key>
```

## Common Headers

```http
Content-Type: application/json
Accept: application/json
X-Request-ID: <unique-request-id>
```

## Response Format

### Success Response

```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "metadata": {
    "request_id": "req-abc-123",
    "timestamp": "2024-12-16T13:30:00Z",
    "processing_time_ms": 245
  }
}
```

### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "field_name",
      "reason": "Detailed reason"
    }
  },
  "metadata": {
    "request_id": "req-abc-123",
    "timestamp": "2024-12-16T13:30:00Z"
  }
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## Endpoints

### 1. Health Check

Check API health status.

**Endpoint**: `GET /health`

**Response**: 200 OK
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-12-16T13:30:00Z"
}
```

---

### 2. Detect Anomalies

Analyze data for anomalies.

**Endpoint**: `POST /api/v1/anomalies/detect`

**Request Body**:
```json
{
  "data": {
    "metric_type": "compute_usage",
    "time_range": {
      "start": "2024-12-01T00:00:00Z",
      "end": "2024-12-15T23:59:59Z"
    },
    "filters": {
      "project_id": "ccibt-hack25ww7-730",
      "resource_type": "compute_instance",
      "region": "us-central1"
    },
    "detection_config": {
      "methods": ["statistical", "ml_based"],
      "sensitivity": "high",
      "min_confidence": 0.75
    }
  }
}
```

**Response**: 200 OK
```json
{
  "status": "success",
  "data": {
    "analysis_id": "analysis-abc-123",
    "anomalies": [
      {
        "id": "anom-123",
        "timestamp": "2024-12-10T14:30:00Z",
        "severity": "high",
        "confidence": 0.92,
        "metric_type": "compute_usage",
        "metric_value": 1250.5,
        "expected_value": 450.2,
        "deviation": 2.8,
        "deviation_percentage": 177.8,
        "detection_method": "z_score",
        "explanation": "Detected 178% increase in compute usage at 14:30 UTC. This represents a 2.8 standard deviation from the expected baseline of 450.2 units.",
        "affected_resources": [
          {
            "resource_id": "instance-xyz-123",
            "resource_type": "compute_instance",
            "region": "us-central1"
          }
        ]
      }
    ],
    "summary": {
      "total_anomalies": 1,
      "by_severity": {
        "critical": 0,
        "high": 1,
        "medium": 0,
        "low": 0
      },
      "time_range_analyzed": {
        "start": "2024-12-01T00:00:00Z",
        "end": "2024-12-15T23:59:59Z"
      }
    }
  },
  "metadata": {
    "request_id": "req-abc-123",
    "timestamp": "2024-12-16T13:30:00Z",
    "processing_time_ms": 1245
  }
}
```

---

### 3. Get Anomaly Details

Retrieve details of a specific anomaly.

**Endpoint**: `GET /api/v1/anomalies/{anomaly_id}`

**Path Parameters**:
- `anomaly_id` (string, required): Unique anomaly identifier

**Response**: 200 OK
```json
{
  "status": "success",
  "data": {
    "id": "anom-123",
    "timestamp": "2024-12-10T14:30:00Z",
    "severity": "high",
    "confidence": 0.92,
    "metric_type": "compute_usage",
    "metric_value": 1250.5,
    "expected_value": 450.2,
    "deviation": 2.8,
    "deviation_percentage": 177.8,
    "detection_method": "z_score",
    "explanation": "Detailed explanation of the anomaly...",
    "affected_resources": [...],
    "correlations": [
      {
        "type": "workload_migration",
        "confidence": 0.85,
        "event_id": "migration-xyz-456",
        "timestamp": "2024-12-10T14:15:00Z",
        "details": "Migration of workload-xyz started at 14:15 UTC",
        "correlation_score": 0.85
      }
    ],
    "recommendations": [
      {
        "priority": "high",
        "action": "Review migration schedule for workload-xyz",
        "rationale": "The spike correlates strongly with the migration event",
        "estimated_impact": "Reduce investigation time by 80%"
      }
    ],
    "historical_context": {
      "similar_anomalies": 2,
      "last_occurrence": "2024-11-15T10:20:00Z",
      "typical_resolution_time": "2 hours"
    }
  },
  "metadata": {
    "request_id": "req-abc-124",
    "timestamp": "2024-12-16T13:31:00Z",
    "processing_time_ms": 156
  }
}
```

---

### 4. List Anomalies

List all detected anomalies with filtering and pagination.

**Endpoint**: `GET /api/v1/anomalies`

**Query Parameters**:
- `start_time` (string, optional): ISO 8601 timestamp
- `end_time` (string, optional): ISO 8601 timestamp
- `severity` (string, optional): critical, high, medium, low
- `metric_type` (string, optional): Filter by metric type
- `resource_type` (string, optional): Filter by resource type
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 20, max: 100)
- `sort_by` (string, optional): timestamp, severity, confidence (default: timestamp)
- `sort_order` (string, optional): asc, desc (default: desc)

**Example Request**:
```
GET /api/v1/anomalies?severity=high&page=1&page_size=20&sort_by=timestamp&sort_order=desc
```

**Response**: 200 OK
```json
{
  "status": "success",
  "data": {
    "anomalies": [
      {
        "id": "anom-123",
        "timestamp": "2024-12-10T14:30:00Z",
        "severity": "high",
        "confidence": 0.92,
        "metric_type": "compute_usage",
        "summary": "178% increase in compute usage"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 45,
      "total_pages": 3,
      "has_next": true,
      "has_previous": false
    }
  },
  "metadata": {
    "request_id": "req-abc-125",
    "timestamp": "2024-12-16T13:32:00Z",
    "processing_time_ms": 89
  }
}
```

---

### 5. Analyze Correlations

Analyze correlations between anomalies and events.

**Endpoint**: `POST /api/v1/correlations/analyze`

**Request Body**:
```json
{
  "data": {
    "anomaly_id": "anom-123",
    "correlation_config": {
      "time_window_minutes": 60,
      "min_confidence": 0.7,
      "event_sources": [
        "workload_migrations",
        "deployments",
        "configuration_changes"
      ]
    }
  }
}
```

**Response**: 200 OK
```json
{
  "status": "success",
  "data": {
    "correlation_id": "corr-abc-789",
    "anomaly_id": "anom-123",
    "correlations": [
      {
        "type": "workload_migration",
        "confidence": 0.85,
        "event_id": "migration-xyz-456",
        "timestamp": "2024-12-10T14:15:00Z",
        "time_difference_minutes": 15,
        "correlation_methods": {
          "temporal": 0.9,
          "statistical": 0.8,
          "pattern": 0.85
        },
        "details": {
          "workload_name": "workload-xyz",
          "source_region": "us-east1",
          "target_region": "us-central1",
          "resources_migrated": 25
        },
        "explanation": "Strong temporal and statistical correlation detected between the anomaly and workload migration event."
      }
    ],
    "summary": {
      "total_correlations": 1,
      "high_confidence": 1,
      "medium_confidence": 0,
      "low_confidence": 0
    }
  },
  "metadata": {
    "request_id": "req-abc-126",
    "timestamp": "2024-12-16T13:33:00Z",
    "processing_time_ms": 567
  }
}
```

---

### 6. Generate Report

Generate a comprehensive analysis report.

**Endpoint**: `POST /api/v1/reports/generate`

**Request Body**:
```json
{
  "data": {
    "report_type": "anomaly_analysis",
    "time_range": {
      "start": "2024-12-01T00:00:00Z",
      "end": "2024-12-15T23:59:59Z"
    },
    "filters": {
      "severity": ["high", "critical"],
      "metric_types": ["compute_usage", "storage_usage"]
    },
    "include_sections": [
      "executive_summary",
      "anomaly_details",
      "correlations",
      "recommendations",
      "cost_impact"
    ],
    "format": "json"
  }
}
```

**Response**: 200 OK
```json
{
  "status": "success",
  "data": {
    "report_id": "report-abc-999",
    "report_type": "anomaly_analysis",
    "generated_at": "2024-12-16T13:34:00Z",
    "time_range": {
      "start": "2024-12-01T00:00:00Z",
      "end": "2024-12-15T23:59:59Z"
    },
    "executive_summary": {
      "total_anomalies": 12,
      "critical_anomalies": 2,
      "high_anomalies": 5,
      "average_resolution_time": "45 minutes",
      "cost_impact": {
        "total_unexpected_cost": 1250.50,
        "currency": "USD"
      },
      "key_findings": [
        "Workload migrations are the primary cause of compute usage spikes",
        "80% of anomalies occur during business hours",
        "Average detection time: 5 minutes"
      ]
    },
    "anomalies": [...],
    "correlations": [...],
    "recommendations": [
      {
        "priority": "high",
        "category": "process_improvement",
        "recommendation": "Implement pre-migration capacity planning",
        "expected_benefit": "Reduce unexpected cost spikes by 60%",
        "implementation_effort": "medium"
      }
    ],
    "download_url": "https://storage.googleapis.com/reports/report-abc-999.pdf"
  },
  "metadata": {
    "request_id": "req-abc-127",
    "timestamp": "2024-12-16T13:34:00Z",
    "processing_time_ms": 2345
  }
}
```

---

### 7. Get Report

Retrieve a previously generated report.

**Endpoint**: `GET /api/v1/reports/{report_id}`

**Path Parameters**:
- `report_id` (string, required): Unique report identifier

**Response**: 200 OK
```json
{
  "status": "success",
  "data": {
    "report_id": "report-abc-999",
    "report_type": "anomaly_analysis",
    "generated_at": "2024-12-16T13:34:00Z",
    "status": "completed",
    "download_url": "https://storage.googleapis.com/reports/report-abc-999.pdf",
    "expires_at": "2024-12-23T13:34:00Z"
  },
  "metadata": {
    "request_id": "req-abc-128",
    "timestamp": "2024-12-16T13:35:00Z",
    "processing_time_ms": 45
  }
}
```

---

### 8. Agent Query

Interactive query to the ADK agent.

**Endpoint**: `POST /api/v1/agent/query`

**Request Body**:
```json
{
  "data": {
    "query": "What caused the compute usage spike on December 10th at 2:30 PM?",
    "context": {
      "conversation_id": "conv-abc-123",
      "user_id": "user-xyz-789"
    },
    "options": {
      "include_recommendations": true,
      "max_response_length": 500
    }
  }
}
```

**Response**: 200 OK
```json
{
  "status": "success",
  "data": {
    "query_id": "query-abc-456",
    "conversation_id": "conv-abc-123",
    "response": {
      "answer": "The compute usage spike on December 10th at 2:30 PM was caused by a workload migration from us-east1 to us-central1. The migration involved 25 compute instances and started at 2:15 PM, which correlates strongly (85% confidence) with the observed spike.",
      "confidence": 0.92,
      "sources": [
        {
          "type": "anomaly_detection",
          "id": "anom-123"
        },
        {
          "type": "correlation_analysis",
          "id": "corr-abc-789"
        }
      ],
      "recommendations": [
        "Review migration schedule to avoid peak hours",
        "Implement gradual migration strategy",
        "Set up proactive alerts for future migrations"
      ],
      "follow_up_questions": [
        "What was the cost impact of this spike?",
        "How can we prevent similar spikes in the future?",
        "Were there any other anomalies during this time period?"
      ]
    },
    "agent_metadata": {
      "model": "gemini-1.5-pro",
      "reasoning_steps": 5,
      "tools_used": ["query_bigquery", "analyze_correlations", "generate_recommendations"]
    }
  },
  "metadata": {
    "request_id": "req-abc-129",
    "timestamp": "2024-12-16T13:36:00Z",
    "processing_time_ms": 1567
  }
}
```

---

### 9. Get Metrics

Retrieve system and business metrics.

**Endpoint**: `GET /api/v1/metrics`

**Query Parameters**:
- `metric_types` (string, optional): Comma-separated list of metric types
- `start_time` (string, optional): ISO 8601 timestamp
- `end_time` (string, optional): ISO 8601 timestamp
- `aggregation` (string, optional): hour, day, week (default: day)

**Response**: 200 OK
```json
{
  "status": "success",
  "data": {
    "metrics": {
      "anomalies_detected": {
        "total": 45,
        "by_severity": {
          "critical": 5,
          "high": 15,
          "medium": 20,
          "low": 5
        },
        "trend": "increasing"
      },
      "detection_performance": {
        "average_detection_time_ms": 5000,
        "average_confidence": 0.87,
        "false_positive_rate": 0.05
      },
      "correlation_accuracy": {
        "high_confidence_correlations": 35,
        "accuracy_rate": 0.92
      },
      "api_performance": {
        "total_requests": 1250,
        "average_response_time_ms": 245,
        "error_rate": 0.02,
        "p95_latency_ms": 450,
        "p99_latency_ms": 890
      },
      "cost_metrics": {
        "total_api_cost": 12.50,
        "total_compute_cost": 45.30,
        "cost_per_analysis": 0.15,
        "currency": "USD"
      }
    },
    "time_range": {
      "start": "2024-12-01T00:00:00Z",
      "end": "2024-12-15T23:59:59Z"
    }
  },
  "metadata": {
    "request_id": "req-abc-130",
    "timestamp": "2024-12-16T13:37:00Z",
    "processing_time_ms": 123
  }
}
```

---

## Data Models

### Anomaly

```json
{
  "id": "string",
  "timestamp": "string (ISO 8601)",
  "severity": "critical | high | medium | low",
  "confidence": "number (0-1)",
  "metric_type": "string",
  "metric_value": "number",
  "expected_value": "number",
  "deviation": "number",
  "deviation_percentage": "number",
  "detection_method": "string",
  "explanation": "string",
  "affected_resources": [
    {
      "resource_id": "string",
      "resource_type": "string",
      "region": "string"
    }
  ],
  "correlations": [...],
  "recommendations": [...]
}
```

### Correlation

```json
{
  "type": "string",
  "confidence": "number (0-1)",
  "event_id": "string",
  "timestamp": "string (ISO 8601)",
  "time_difference_minutes": "number",
  "correlation_methods": {
    "temporal": "number (0-1)",
    "statistical": "number (0-1)",
    "pattern": "number (0-1)"
  },
  "details": "object",
  "explanation": "string"
}
```

### Recommendation

```json
{
  "priority": "critical | high | medium | low",
  "category": "string",
  "action": "string",
  "rationale": "string",
  "estimated_impact": "string",
  "implementation_effort": "low | medium | high"
}
```

---

## Rate Limits

- **Default**: 100 requests per minute per API key
- **Burst**: 200 requests per minute (short bursts allowed)
- **Daily**: 10,000 requests per day per API key

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1702742400
```

---

## Webhooks

Configure webhooks to receive real-time notifications.

### Webhook Events

- `anomaly.detected`: New anomaly detected
- `anomaly.resolved`: Anomaly resolved
- `correlation.found`: High-confidence correlation found
- `report.generated`: Report generation completed

### Webhook Payload

```json
{
  "event": "anomaly.detected",
  "timestamp": "2024-12-16T13:38:00Z",
  "data": {
    "anomaly_id": "anom-123",
    "severity": "high",
    "metric_type": "compute_usage",
    "summary": "178% increase in compute usage"
  }
}
```

---

## SDK Examples

### Python

```python
from anomaly_detection_client import AnomalyDetectionClient

client = AnomalyDetectionClient(
    api_key="your-api-key",
    base_url="https://api.example.com"
)

# Detect anomalies
result = client.detect_anomalies(
    metric_type="compute_usage",
    time_range={
        "start": "2024-12-01T00:00:00Z",
        "end": "2024-12-15T23:59:59Z"
    }
)

# Get anomaly details
anomaly = client.get_anomaly("anom-123")

# Analyze correlations
correlations = client.analyze_correlations(
    anomaly_id="anom-123",
    time_window_minutes=60
)

# Query agent
response = client.query_agent(
    "What caused the spike on December 10th?"
)
```

### cURL

```bash
# Detect anomalies
curl -X POST https://api.example.com/api/v1/anomalies/detect \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "metric_type": "compute_usage",
      "time_range": {
        "start": "2024-12-01T00:00:00Z",
        "end": "2024-12-15T23:59:59Z"
      }
    }
  }'

# Get anomaly
curl -X GET https://api.example.com/api/v1/anomalies/anom-123 \
  -H "Authorization: Bearer your-api-key"
```

---

## OpenAPI/Swagger

The complete OpenAPI 3.0 specification is available at:
- **JSON**: `/api/v1/openapi.json`
- **YAML**: `/api/v1/openapi.yaml`
- **Interactive Docs**: `/api/v1/docs`

---

**Document Version**: 1.0  
**Last Updated**: 2024-12-16  
**Maintained By**: Hackathon Team