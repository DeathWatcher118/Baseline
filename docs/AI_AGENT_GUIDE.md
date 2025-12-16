# AI Agent for Anomaly Analysis - Complete Guide

## Overview

The **AnomalyAnalyzerAgent** is an AI-powered system that analyzes detected anomalies and provides:
- **Context**: What the anomaly is and its characteristics
- **Root Cause**: Why the anomaly occurred
- **Recommendations**: What should be done to address it
- **Impact Assessment**: Consequences if not addressed

**Note**: The AnomalyAnalyzerAgent focuses solely on analysis. Notification delivery is handled by a separate Notification System component.

## Key Features

### 1. Intelligent Analysis
- Uses Vertex AI Gemini for deep analysis
- Contextual understanding of anomalies
- Historical pattern recognition
- Correlation with system events

### 2. Type-Specific Recommendations

#### Stability Issues
- Identifies system instability causes
- Recommends resilience improvements
- Suggests error handling enhancements
- Provides monitoring strategies

#### Performance Issues
- Analyzes performance bottlenecks
- Recommends optimization strategies
- Suggests scaling approaches
- Identifies inefficiencies

#### Cost Issues
- Identifies waste and over-provisioning
- Recommends cost-saving measures
- **Explains why changes won't impact performance**
- Provides cost-benefit analysis

### 3. Actionable Recommendations
- Prioritized by urgency and impact
- Step-by-step implementation guides
- Effort estimates
- Risk assessments

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Anomaly Detection                         │
│              (Baseline Calculator Module)                    │
└────────────────────┬────────────────────────────────────────┘
                     │ Anomaly Detected
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              AnomalyAnalyzerAgent                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Context Gathering                                 │  │
│  │     - Historical data                                 │  │
│  │     - Related metrics                                 │  │
│  │     - Recent changes                                  │  │
│  │     - Trend analysis                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  2. Root Cause Analysis (AI-Powered)                 │  │
│  │     - Vertex AI Gemini analysis                      │  │
│  │     - Pattern recognition                            │  │
│  │     - Correlation detection                          │  │
│  │     - Evidence gathering                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  3. Recommendation Generation (Type-Specific)        │  │
│  │     - Stability: Resilience improvements             │  │
│  │     - Performance: Optimization strategies           │  │
│  │     - Cost: Savings with performance analysis        │  │
│  └──────────────────────────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  4. Impact Assessment & Persistence                  │  │
│  │     - Severity-based predictions                     │  │
│  │     - Timeline estimates                             │  │
│  │     - Risk evaluation                                │  │
│  │     - Save to BigQuery                               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ Analysis Saved to BigQuery
                     │ (AnomalyAnalysis object)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Notification System (Separate Component)        │
│                                                              │
│  - Monitors BigQuery for new analyses                       │
│  - Routes notifications by severity/type                    │
│  - Supports multiple channels (Slack, Email, PagerDuty)     │
│  - Handles delivery retries and failures                    │
│  - Manages alert deduplication                              │
│                                                              │
│  See: docs/NOTIFICATION_SYSTEM.md                           │
└─────────────────────────────────────────────────────────────┘
```

## Component Separation

### AnomalyAnalyzerAgent Responsibilities
✅ Analyze anomalies with AI
✅ Determine root causes
✅ Generate recommendations
✅ Save analysis to BigQuery
✅ Provide structured output (AnomalyAnalysis object)

### Notification System Responsibilities (Separate Component)
✅ Monitor for new analyses
✅ Route notifications by severity
✅ Deliver to multiple channels
✅ Handle retries and failures
✅ Manage alert deduplication
✅ Track delivery status

**Why Separate?**
- **Single Responsibility**: Each component has one clear purpose
- **Scalability**: Notification system can scale independently
- **Flexibility**: Easy to add new notification channels
- **Reliability**: Notification failures don't affect analysis
- **Testing**: Easier to test components in isolation

## Data Models

### Anomaly
```python
@dataclass
class Anomaly:
    anomaly_id: str
    detected_at: datetime
    metric_name: str
    current_value: float
    baseline_value: float
    deviation_sigma: float
    deviation_percentage: float
    anomaly_type: AnomalyType  # STABILITY, PERFORMANCE, COST
    severity: Severity  # CRITICAL, HIGH, MEDIUM, LOW
    confidence: float
    affected_resources: List[Dict]
    related_metrics: Dict[str, float]
```

### RootCause
```python
@dataclass
class RootCause:
    primary_cause: str
    contributing_factors: List[str]
    confidence: float
    evidence: List[str]
    correlation_data: Dict[str, Any]
```

### Recommendation
```python
@dataclass
class Recommendation:
    priority: str  # critical, high, medium, low
    action: str  # What to do
    rationale: str  # Why
    expected_impact: str  # What will improve
    implementation_steps: List[str]
    estimated_effort: str
    risk_level: str
    cost_impact: Optional[str]  # For cost recommendations
```

### AnomalyAnalysis
```python
@dataclass
class AnomalyAnalysis:
    anomaly: Anomaly
    root_cause: RootCause
    recommendations: List[Recommendation]
    analyzed_at: datetime
    analysis_duration_ms: int
    ai_model_used: str
    historical_context: str
    trend_analysis: str
    predicted_impact: str
```

## Usage Examples

### Example 1: Analyze Stability Issue

```python
from src.agent.anomaly_analyzer import AnomalyAnalyzerAgent
from src.models.anomaly import Anomaly, AnomalyType, Severity
from datetime import datetime

# Create anomaly (from detection system)
anomaly = Anomaly(
    anomaly_id="anom-001",
    detected_at=datetime.now(),
    metric_name="error_rate",
    metric_type="Error_Rate _%_",
    current_value=45.0,
    baseline_value=22.8,
    deviation_sigma=5.3,
    deviation_percentage=97.4,
    anomaly_type=AnomalyType.STABILITY,
    severity=Severity.CRITICAL,
    confidence=0.95,
    affected_resources=[
        {"job_id": "JOB_1234", "machine_id": "MACH_890"}
    ]
)

# Analyze with AI agent
agent = AnomalyAnalyzerAgent()
analysis = agent.analyze_anomaly(anomaly)

# Access results
print(f"Root Cause: {analysis.root_cause.primary_cause}")
print(f"Confidence: {analysis.root_cause.confidence:.0%}")

for rec in analysis.recommendations:
    print(f"\n[{rec.priority.upper()}] {rec.action}")
    print(f"Impact: {rec.expected_impact}")
    print(f"Steps:")
    for step in rec.implementation_steps:
        print(f"  - {step}")
```

**Output:**
```
Root Cause: Elevated error rate indicating system instability due to resource contention
Confidence: 92%

[HIGH] Investigate and address elevated error_rate
Impact: Restore system stability and prevent cascading failures
Steps:
  - Review recent logs for error patterns
  - Check for resource constraints
  - Verify configuration changes
  - Implement additional error handling

[MEDIUM] Implement enhanced monitoring and alerting
Impact: Faster incident response and reduced downtime
Steps:
  - Set up alerts for error rate thresholds
  - Configure log aggregation
  - Create dashboard for key metrics
```

### Example 2: Analyze Performance Issue

```python
anomaly = Anomaly(
    anomaly_id="anom-002",
    detected_at=datetime.now(),
    metric_name="task_execution_time",
    metric_type="Task_Execution_Time _ms_",
    current_value=850.0,
    baseline_value=320.0,
    deviation_sigma=4.2,
    deviation_percentage=165.6,
    anomaly_type=AnomalyType.PERFORMANCE,
    severity=Severity.HIGH,
    confidence=0.88
)

analysis = agent.analyze_anomaly(anomaly)

# AI provides performance-specific recommendations
for rec in analysis.recommendations:
    print(f"{rec.action}")
    print(f"Expected: {rec.expected_impact}")
```

**Output:**
```
Optimize resource allocation
Expected: Improve response times by 20-40%

Review and optimize queries/operations
Expected: Reduce latency and improve throughput
```

### Example 3: Analyze Cost Issue

```python
anomaly = Anomaly(
    anomaly_id="anom-003",
    detected_at=datetime.now(),
    metric_name="compute_cost",
    metric_type="Cost_USD",
    current_value=1250.0,
    baseline_value=650.0,
    deviation_sigma=3.8,
    deviation_percentage=92.3,
    anomaly_type=AnomalyType.COST,
    severity=Severity.MEDIUM,
    confidence=0.91
)

analysis = agent.analyze_anomaly(anomaly)

# AI explains why cost savings won't impact performance
for rec in analysis.recommendations:
    print(f"{rec.action}")
    print(f"Cost Impact: {rec.cost_impact}")
```

**Output:**
```
Right-size over-provisioned resources
Cost Impact: Save $600/month with no performance impact because current CPU utilization averages 15% and memory usage is at 22%, well below the 70% threshold where performance degradation begins.

Implement auto-scaling policies
Cost Impact: Save 30-50% on compute costs during low-traffic periods while maintaining performance during peak hours through automatic scaling.
```

## Output Format

The AnomalyAnalyzerAgent produces a structured `AnomalyAnalysis` object that is saved to BigQuery. The Notification System (separate component) monitors this table and handles delivery.

### Analysis Output Structure

```python
{
    "analysis_id": "uuid",
    "anomaly": {
        "anomaly_id": "anom-001",
        "detected_at": "2025-12-16T16:00:00Z",
        "metric_name": "error_rate",
        "current_value": 45.0,
        "baseline_value": 22.8,
        "deviation_sigma": 5.3,
        "deviation_percentage": 97.4,
        "anomaly_type": "STABILITY",
        "severity": "CRITICAL",
        "confidence": 0.95
    },
    "root_cause": {
        "primary_cause": "Elevated error rate due to resource contention",
        "contributing_factors": ["High CPU usage", "Memory pressure"],
        "confidence": 0.92,
        "evidence": ["Error logs show timeout patterns", "CPU at 95%"]
    },
    "recommendations": [
        {
            "priority": "high",
            "action": "Investigate and address elevated error_rate",
            "rationale": "Prevent cascading failures",
            "expected_impact": "Restore system stability",
            "implementation_steps": ["Review logs", "Check resources"],
            "estimated_effort": "2-4 hours",
            "risk_level": "low"
        }
    ],
    "analyzed_at": "2025-12-16T16:00:05Z",
    "analysis_duration_ms": 1250,
    "ai_model_used": "gemini-1.5-pro"
}
```

### BigQuery Table Schema

```sql
CREATE TABLE `ccibt-hack25ww7-730.hackaton.AnomalyAnalysis` (
    analysis_id STRING NOT NULL,
    anomaly_id STRING NOT NULL,
    analyzed_at TIMESTAMP NOT NULL,
    anomaly STRUCT<
        anomaly_id STRING,
        detected_at TIMESTAMP,
        metric_name STRING,
        current_value FLOAT64,
        baseline_value FLOAT64,
        deviation_sigma FLOAT64,
        deviation_percentage FLOAT64,
        anomaly_type STRING,
        severity STRING,
        confidence FLOAT64
    >,
    root_cause STRUCT<
        primary_cause STRING,
        contributing_factors ARRAY<STRING>,
        confidence FLOAT64,
        evidence ARRAY<STRING>
    >,
    recommendations ARRAY<STRUCT<
        priority STRING,
        action STRING,
        rationale STRING,
        expected_impact STRING,
        implementation_steps ARRAY<STRING>,
        estimated_effort STRING,
        risk_level STRING,
        cost_impact STRING
    >>,
    analysis_duration_ms INT64,
    ai_model_used STRING,
    notified BOOLEAN DEFAULT FALSE,
    notification_attempts INT64 DEFAULT 0
);
```

## Integration with Notification System

The AnomalyAnalyzerAgent and Notification System communicate via BigQuery:

```
┌──────────────────────┐
│ AnomalyAnalyzerAgent │
│                      │
│ 1. Analyze anomaly   │
│ 2. Generate insights │
│ 3. Save to BigQuery  │
└──────────┬───────────┘
           │
           │ Writes AnomalyAnalysis
           ▼
┌──────────────────────┐
│      BigQuery        │
│  AnomalyAnalysis     │
│       Table          │
└──────────┬───────────┘
           │
           │ Polls for new analyses
           │ (notified = FALSE)
           ▼
┌──────────────────────┐
│ Notification System  │
│  (Separate Service)  │
│                      │
│ 1. Query new records │
│ 2. Route by severity │
│ 3. Send notifications│
│ 4. Update notified   │
└──────────────────────┘
```

### Example: Querying for New Analyses

The Notification System queries for unnotified analyses:

```python
# In Notification System (separate component)
from google.cloud import bigquery

def get_pending_notifications():
    """Query for analyses that need notification"""
    client = bigquery.Client()
    
    query = """
    SELECT 
        analysis_id,
        anomaly_id,
        anomaly.severity,
        anomaly.anomaly_type,
        root_cause.primary_cause,
        recommendations
    FROM `ccibt-hack25ww7-730.hackaton.AnomalyAnalysis`
    WHERE notified = FALSE
    ORDER BY analyzed_at DESC
    """
    
    return list(client.query(query).result())

def mark_as_notified(analysis_id: str):
    """Mark analysis as notified"""
    client = bigquery.Client()
    
    query = f"""
    UPDATE `ccibt-hack25ww7-730.hackaton.AnomalyAnalysis`
    SET 
        notified = TRUE,
        notification_attempts = notification_attempts + 1
    WHERE analysis_id = '{analysis_id}'
    """
    
    client.query(query).result()
```

For complete Notification System implementation, see: **`docs/NOTIFICATION_SYSTEM.md`**

## Configuration

Add to `config.yaml`:

```yaml
anomaly_analysis:
  # AI settings
  use_ai: true
  ai_confidence_threshold: 0.75
  
  # Analysis settings
  context_window_hours: 24
  max_recommendations: 4
  
  # BigQuery output
  output_table: "ccibt-hack25ww7-730.hackaton.AnomalyAnalysis"
  
  # Note: Notification settings are in the separate Notification System
  # See docs/NOTIFICATION_SYSTEM.md for notification configuration
```

## Deployment

### Update Dockerfile

The agent is already included in the baseline calculator deployment. No changes needed.

### Environment Variables

```bash
# Add to Cloud Run deployment
gcloud run services update baseline-calculator \
    --update-env-vars "ENABLE_ANOMALY_ANALYSIS=true" \
    --region us-central1

# Notification System is deployed separately
# See docs/NOTIFICATION_SYSTEM.md for its deployment
```

## Testing

### Unit Test

```python
# tests/test_anomaly_analyzer.py
import pytest
from src.agent.anomaly_analyzer import AnomalyAnalyzerAgent
from src.models.anomaly import Anomaly, AnomalyType, Severity
from datetime import datetime

def test_analyze_stability_anomaly():
    agent = AnomalyAnalyzerAgent()
    
    anomaly = Anomaly(
        anomaly_id="test-001",
        detected_at=datetime.now(),
        metric_name="error_rate",
        metric_type="Error_Rate _%_",
        current_value=45.0,
        baseline_value=22.8,
        deviation_sigma=5.3,
        deviation_percentage=97.4,
        anomaly_type=AnomalyType.STABILITY,
        severity=Severity.CRITICAL,
        confidence=0.95
    )
    
    analysis = agent.analyze_anomaly(anomaly)
    
    assert analysis.root_cause is not None
    assert len(analysis.recommendations) > 0
    assert analysis.recommendations[0].priority in ["critical", "high"]
```

## Best Practices

### 1. Anomaly Classification
- Accurately classify anomaly type (stability/performance/cost)
- Set appropriate severity levels
- Include confidence scores

### 2. Context Gathering
- Provide historical data when available
- Include related metrics
- Note recent system changes

### 3. Recommendation Quality
- Prioritize by impact and urgency
- Provide specific, actionable steps
- Include effort estimates
- Assess risks

### 4. Output Quality
- Save complete analysis to BigQuery
- Include all context and evidence
- Ensure recommendations are actionable
- Provide confidence scores

**Note**: Notification routing is handled by the separate Notification System component

## Monitoring

### Track Agent Performance

```python
# Log analysis metrics
logger.info(f"Analysis completed", extra={
    'anomaly_id': analysis.anomaly.anomaly_id,
    'duration_ms': analysis.analysis_duration_ms,
    'recommendations_count': len(analysis.recommendations),
    'root_cause_confidence': analysis.root_cause.confidence,
    'ai_model': analysis.ai_model_used
})
```

### Query Analysis History

```sql
-- View recent analyses
SELECT 
    analysis_id,
    anomaly_id,
    analyzed_at,
    root_cause.primary_cause as root_cause,
    root_cause.confidence,
    JSON_EXTRACT(recommendations, '$[0].priority') as top_priority
FROM `ccibt-hack25ww7-730.hackaton.AnomalyAnalysis`
ORDER BY analyzed_at DESC
LIMIT 10
```

## Troubleshooting

### Issue: AI Analysis Fails
**Solution**: Agent automatically falls back to rule-based analysis

### Issue: No Recommendations Generated
**Solution**: Check anomaly classification and severity

### Issue: Analysis Not Appearing in BigQuery
**Solution**: Check BigQuery permissions and table schema

### Issue: Notifications Not Sending
**Solution**: This is handled by the Notification System component. See `docs/NOTIFICATION_SYSTEM.md`

---

## Related Documentation

- **Notification System**: `docs/NOTIFICATION_SYSTEM.md` - Separate component for alert delivery
- **Baseline Calculator**: `docs/BASELINE_CALCULATOR.md` - Anomaly detection system
- **Architecture**: `docs/architecture/MVP_ARCHITECTURE.md` - Overall system design

---

**The AI Agent is production-ready and provides intelligent, actionable insights for every anomaly detected! Notification delivery is handled by a separate, scalable Notification System component.**