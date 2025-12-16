# Migration Analysis in Anomaly Detection

## Overview

The AI Agent automatically analyzes **migration events** to determine if they caused or contributed to detected anomalies. This is critical because migrations are a common source of system issues:

- **User Migrations**: Adding users increases system load
- **Functionality Changes**: New features require more resources
- **Configuration Changes**: Can cause unexpected behavior
- **Resource Requirement Changes**: May exceed capacity

## How It Works

### 1. Migration Data Collection

When an anomaly is detected, the AI Agent queries the `migrations` table in BigQuery for events within 24 hours before the anomaly:

```sql
SELECT 
    migration_id,
    migration_type,
    migration_timestamp,
    source_system,
    target_system,
    user_count_change,
    resource_requirements,
    description,
    status
FROM `ccibt-hack25ww7-730.hackaton.migrations`
WHERE migration_timestamp BETWEEN @start_time AND @end_time
ORDER BY migration_timestamp DESC
```

### 2. Impact Analysis

For each migration found, the system analyzes:

#### User Count Changes
```python
if migration['user_count_change'] > 0:
    # Increased users = increased load
    impact = f"Added {user_count_change} users, increasing system load"
```

#### Functionality Changes
```python
if 'functionality' in migration_type or 'feature' in migration_type:
    # New features may need more resources
    impact = "New functionality may require additional resources"
```

#### Resource Requirements
```python
resource_reqs = migration['resource_requirements']
if resource_reqs.get('cpu_increase'):
    impact = f"Requires {cpu_increase}% more CPU"
if resource_reqs.get('memory_increase'):
    impact = f"Requires {memory_increase}% more memory"
```

### 3. Temporal Correlation

The system checks timing between migration and anomaly:

```python
time_diff_hours = (anomaly_detected_at - migration_timestamp).total_seconds() / 3600

if time_diff_hours < 6:
    # Migration occurred within 6 hours - LIKELY CAUSE
    likely_cause = True
elif time_diff_hours < 24:
    # Migration occurred within 24 hours - POSSIBLE CONTRIBUTOR
    likely_cause = False
```

### 4. Root Cause Integration

Migration analysis is integrated into the root cause explanation:

```
WHY IT HAPPENED:
Elevated error rate indicating system instability due to resource contention.

Several factors contributed to this issue:
1. High CPU usage at 95.2%
2. Memory pressure at 87.5%
3. Increased request rate to 1250 requests/second

**Migration Event Detected:**
Found 1 recent migration(s) that likely contributed to this anomaly. The migration(s) 
occurred shortly before the anomaly was detected and involved changes that could explain 
the observed behavior: User migration added 500 users 2.3h before anomaly; New 
functionality deployed 2.3h before anomaly

Specific changes that may have caused this:
• User migration added 500 users 2.3h before anomaly
• New functionality deployed 2.3h before anomaly
• Resource requirements changed 2.3h before anomaly

We are very confident (92%) in this assessment based on the available data.
```

## Migration Table Schema

### Required Fields

```sql
CREATE TABLE `ccibt-hack25ww7-730.hackaton.migrations` (
    migration_id STRING NOT NULL,
    migration_type STRING NOT NULL,
    migration_timestamp TIMESTAMP NOT NULL,
    source_system STRING,
    target_system STRING,
    status STRING NOT NULL,
    
    -- Optional but highly recommended
    user_count_change INT64,
    resource_requirements JSON,
    description STRING
);
```

### Example Migration Records

#### User Migration
```json
{
    "migration_id": "MIG-2025-001",
    "migration_type": "user_migration",
    "migration_timestamp": "2025-12-16T14:00:00Z",
    "source_system": "legacy_system",
    "target_system": "cloud_platform",
    "user_count_change": 500,
    "resource_requirements": {
        "cpu_increase": 25,
        "memory_increase": 30
    },
    "description": "Migrated 500 users from legacy system",
    "status": "completed"
}
```

#### Functionality Change
```json
{
    "migration_id": "MIG-2025-002",
    "migration_type": "functionality_update",
    "migration_timestamp": "2025-12-16T14:00:00Z",
    "source_system": "v1.0",
    "target_system": "v2.0",
    "user_count_change": 0,
    "resource_requirements": {
        "cpu_increase": 15,
        "memory_increase": 20,
        "storage_increase": 50
    },
    "description": "Added real-time analytics feature",
    "status": "completed"
}
```

## Example Analysis Output

### Scenario: Performance Degradation After User Migration

**Input:**
- Anomaly: Task execution time increased from 320ms to 850ms
- Migration: 500 users added 2 hours before anomaly
- Resource requirements: +25% CPU, +30% memory

**Output:**

```
WHAT HAPPENED:
We detected an unusual spike in your system's task completion time. The task completion 
time increased to 850ms, which is 166% higher than the normal level of 320ms. This change 
is significant - it's 4.2 times larger than typical variations we see.

WHY IT HAPPENED:
Performance degradation caused by increased system load following user migration.

Several factors contributed to this issue:
1. 500 new users added to the system
2. CPU usage increased to 78.5% (up from typical 45%)
3. Memory usage increased to 65.2% (up from typical 40%)

**Migration Event Detected:**
Found 1 recent migration that likely contributed to this anomaly. The migration occurred 
2.0 hours before the anomaly was detected and involved changes that could explain the 
observed behavior: User migration added 500 users 2.0h before anomaly

Specific changes that may have caused this:
• User migration added 500 users 2.0h before anomaly
• Resource requirements changed: +25% CPU, +30% memory

We are very confident (91%) in this assessment based on the available data.

WHAT IS THE IMPACT:
Performance has degraded noticeably. Users are experiencing slow response times that are 
frustrating and may lead to reduced engagement or lost business opportunities.

WHAT IMPROVEMENTS CAN BE MADE:
🔴 **HIGH PRIORITY**: Scale resources to accommodate new user load
   Why: The migration added 500 users but resources weren't scaled accordingly
   How to do it:
   • Increase compute instances by 30% to match new user count
   • Implement auto-scaling based on user load
   • Monitor resource utilization and adjust as needed
   Time needed: 1-2 hours

🟠 **HIGH PRIORITY**: Optimize for increased user base
   Why: Ensure system can handle current and future user growth
   How to do it:
   • Review and optimize database queries for scale
   • Implement caching for frequently accessed data
   • Load test with projected user growth
   Time needed: 4-8 hours

ESTIMATED BENEFIT IF IMPLEMENTED:
**Faster Response Times**: Scaling resources will bring response times back to normal 
levels around 320ms or better, improving user experience for all 500 new users plus 
existing users.

**Prepared for Growth**: These optimizations will ensure the system can handle future 
user migrations smoothly without performance degradation.

**Quick Wins**: Resource scaling can be implemented within 1-2 hours and will show 
immediate performance improvements.
```

## Benefits of Migration Analysis

✅ **Root Cause Identification**: Quickly identifies if migrations caused issues
✅ **Proactive Planning**: Helps plan resource scaling for future migrations
✅ **Clear Explanations**: Links system behavior to specific migration events
✅ **Actionable Insights**: Provides specific recommendations based on migration type
✅ **Prevents Recurrence**: Identifies patterns to avoid in future migrations

## Best Practices

### 1. Record All Migrations
Always log migrations to the BigQuery table:
```python
from google.cloud import bigquery
from datetime import datetime

def log_migration(migration_data):
    client = bigquery.Client()
    table_id = "ccibt-hack25ww7-730.hackaton.migrations"
    
    rows_to_insert = [{
        "migration_id": migration_data["id"],
        "migration_type": migration_data["type"],
        "migration_timestamp": datetime.now().isoformat(),
        "user_count_change": migration_data.get("users_added", 0),
        "resource_requirements": migration_data.get("resources", {}),
        "description": migration_data["description"],
        "status": "completed"
    }]
    
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"Errors: {errors}")
```

### 2. Include Resource Requirements
Always specify resource impacts:
```json
{
    "resource_requirements": {
        "cpu_increase": 25,      // Percentage increase
        "memory_increase": 30,   // Percentage increase
        "storage_increase": 50,  // Percentage increase
        "network_increase": 15   // Percentage increase
    }
}
```

### 3. Detailed Descriptions
Provide clear descriptions:
```
Good: "Migrated 500 enterprise users from legacy CRM system, including historical data"
Bad: "User migration"
```

### 4. Monitor Post-Migration
Watch for anomalies in the 24 hours after migration:
- Performance metrics
- Error rates
- Resource utilization
- Cost changes

## Integration with Anomaly Detection

The migration analysis is automatically included in every anomaly analysis:

```python
from src.agent.anomaly_analyzer import AnomalyAnalyzerAgent

agent = AnomalyAnalyzerAgent()
analysis = agent.analyze_anomaly(anomaly)

# Migration analysis is included in the output
if analysis.root_cause.correlation_data.get('migration_analysis', {}).get('likely_cause'):
    print("Migration likely caused this anomaly!")
    print(analysis.root_cause.correlation_data['migration_analysis']['impact_summary'])
```

## Summary

Migration analysis is a critical feature that:
- Automatically checks for recent migrations when anomalies occur
- Analyzes user additions, functionality changes, and resource impacts
- Provides clear explanations of how migrations caused issues
- Offers specific recommendations to address migration-related problems
- Helps prevent similar issues in future migrations

**Always log your migrations to enable this powerful analysis capability!**