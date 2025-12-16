# User Feedback System for Anomaly Analysis

## Overview

The AI Agent saves all anomaly analyses to BigQuery with **user feedback fields** that allow reviewers to mark false positives. This creates a feedback loop that helps track and improve the reliability of the analysis over time.

## How It Works

### 1. Analysis Storage

Every time the AI Agent analyzes an anomaly, it saves the complete analysis to:
```
Table: ccibt-hack25ww7-730.hackaton.anomaly_analysis
```

### 2. User Review Process

Users review anomalies and provide feedback:
- **Mark as False Positive**: Anomaly was incorrectly detected
- **Mark as True Positive**: Anomaly was correctly detected
- **Add Review Notes**: Explain why it's a false positive
- **Categorize**: Select reason for false positive

### 3. Reliability Tracking

The system calculates:
- **False Positive Rate**: Percentage of analyses marked as false positives
- **Reliability Score**: 1.0 - false_positive_rate
- **Trends**: Track improvement over time
- **By Type/Severity**: Identify which types need improvement

## Database Schema

### Main Table: `anomaly_analysis`

```sql
CREATE TABLE anomaly_analysis (
    -- Analysis identification
    analysis_id STRING NOT NULL,
    anomaly_id STRING NOT NULL,
    analyzed_at TIMESTAMP NOT NULL,
    
    -- Anomaly details
    metric_name STRING,
    anomaly_type STRING,  -- stability, performance, cost
    severity STRING,  -- critical, high, medium, low
    
    -- Analysis results
    root_cause_primary STRING,
    recommendations JSON,
    summary_what_happened STRING,
    summary_why_happened STRING,
    
    -- USER FEEDBACK FIELDS
    is_false_positive BOOL,  -- NULL=not reviewed, TRUE=false positive, FALSE=true positive
    reviewed_by STRING,  -- User email/ID
    reviewed_at TIMESTAMP,  -- Review timestamp
    review_notes STRING,  -- User comments
    feedback_category STRING  -- Why false positive
);
```

### Feedback Categories

When marking as false positive, users select a category:

| Category | Description | Example |
|----------|-------------|---------|
| `expected_behavior` | This is normal system behavior | Planned maintenance window |
| `incorrect_baseline` | Baseline calculation was wrong | Seasonal pattern not accounted for |
| `data_quality` | Data issue, not real anomaly | Missing data points |
| `migration_related` | Expected due to migration | Known impact from user migration |
| `other` | Other reason | Specify in review_notes |

## User Interface Examples

### Example 1: Review Anomalies (SQL Query)

```sql
-- Get unreviewed anomalies for review
SELECT 
    analysis_id,
    anomaly_id,
    analyzed_at,
    metric_name,
    anomaly_type,
    severity,
    summary_what_happened,
    summary_why_happened,
    summary_impact
FROM `ccibt-hack25ww7-730.hackaton.anomaly_analysis`
WHERE is_false_positive IS NULL
ORDER BY analyzed_at DESC
LIMIT 20;
```

### Example 2: Mark as False Positive

```sql
-- Mark an anomaly as false positive
UPDATE `ccibt-hack25ww7-730.hackaton.anomaly_analysis`
SET 
    is_false_positive = TRUE,
    reviewed_by = 'user@company.com',
    reviewed_at = CURRENT_TIMESTAMP(),
    review_notes = 'This was expected behavior during planned maintenance',
    feedback_category = 'expected_behavior'
WHERE analysis_id = 'your-analysis-id';
```

### Example 3: Mark as True Positive

```sql
-- Confirm an anomaly as true positive
UPDATE `ccibt-hack25ww7-730.hackaton.anomaly_analysis`
SET 
    is_false_positive = FALSE,
    reviewed_by = 'user@company.com',
    reviewed_at = CURRENT_TIMESTAMP(),
    review_notes = 'Confirmed - this was a real issue that needed attention'
WHERE analysis_id = 'your-analysis-id';
```

## Reliability Metrics

### Calculate False Positive Rate

```python
from src.agent.anomaly_analyzer import AnomalyAnalyzerAgent

agent = AnomalyAnalyzerAgent()

# Get false positive rate for last 30 days
stats = agent.get_false_positive_rate(days=30)

print(f"Total Analyses: {stats['total_analyses']}")
print(f"False Positives: {stats['false_positives']}")
print(f"True Positives: {stats['true_positives']}")
print(f"Not Reviewed: {stats['not_reviewed']}")
print(f"False Positive Rate: {stats['false_positive_rate']:.1%}")
print(f"Reliability Score: {stats['reliability_score']:.1%}")

# By type
print("\nBy Anomaly Type:")
for atype, count in stats['by_type'].items():
    print(f"  {atype}: {count} false positives")

# By severity
print("\nBy Severity:")
for severity, count in stats['by_severity'].items():
    print(f"  {severity}: {count} false positives")
```

### View Reliability Dashboard

```sql
-- Daily reliability metrics
SELECT 
    analysis_date,
    total_analyses,
    false_positives,
    true_positives,
    unreviewed,
    ROUND(daily_fp_rate * 100, 1) as fp_rate_pct,
    ROUND((1 - daily_fp_rate) * 100, 1) as reliability_pct
FROM `ccibt-hack25ww7-730.hackaton.analysis_reliability`
ORDER BY analysis_date DESC
LIMIT 30;
```

### False Positive Analysis by Type

```sql
-- Which types have highest false positive rates?
SELECT 
    anomaly_type,
    severity,
    total_count,
    false_positive_count,
    true_positive_count,
    ROUND(false_positive_rate * 100, 1) as fp_rate_pct,
    ROUND(reliability_score * 100, 1) as reliability_pct
FROM `ccibt-hack25ww7-730.hackaton.false_positive_stats`
ORDER BY false_positive_rate DESC;
```

## Using Feedback to Improve Analysis

### 1. Identify Patterns in False Positives

```sql
-- What are common reasons for false positives?
SELECT 
    feedback_category,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
FROM `ccibt-hack25ww7-730.hackaton.anomaly_analysis`
WHERE is_false_positive = TRUE
GROUP BY feedback_category
ORDER BY count DESC;
```

### 2. Analyze False Positives by Metric

```sql
-- Which metrics have most false positives?
SELECT 
    metric_name,
    COUNT(*) as total_analyses,
    COUNTIF(is_false_positive = TRUE) as false_positives,
    ROUND(SAFE_DIVIDE(COUNTIF(is_false_positive = TRUE), 
                      COUNTIF(is_false_positive IS NOT NULL)) * 100, 1) as fp_rate_pct
FROM `ccibt-hack25ww7-730.hackaton.anomaly_analysis`
WHERE is_false_positive IS NOT NULL
GROUP BY metric_name
HAVING COUNT(*) >= 5  -- At least 5 analyses
ORDER BY fp_rate_pct DESC;
```

### 3. Review Notes for Insights

```sql
-- Read user feedback to understand issues
SELECT 
    analyzed_at,
    metric_name,
    anomaly_type,
    severity,
    feedback_category,
    review_notes,
    reviewed_by
FROM `ccibt-hack25ww7-730.hackaton.anomaly_analysis`
WHERE is_false_positive = TRUE
  AND review_notes IS NOT NULL
ORDER BY analyzed_at DESC
LIMIT 50;
```

## Integration with Web UI

### Example: Simple Review Interface (HTML/JavaScript)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Anomaly Review Dashboard</title>
</head>
<body>
    <h1>Unreviewed Anomalies</h1>
    
    <div id="anomalies">
        <!-- Populated from BigQuery -->
    </div>
    
    <script>
    async function loadAnomalies() {
        // Query BigQuery for unreviewed anomalies
        const query = `
            SELECT * FROM \`ccibt-hack25ww7-730.hackaton.unreviewed_anomalies\`
            LIMIT 10
        `;
        
        // Display each anomaly with review buttons
        anomalies.forEach(anomaly => {
            displayAnomaly(anomaly);
        });
    }
    
    function displayAnomaly(anomaly) {
        const div = document.createElement('div');
        div.innerHTML = `
            <h3>${anomaly.metric_name} - ${anomaly.severity}</h3>
            <p><strong>What Happened:</strong> ${anomaly.summary_what_happened}</p>
            <p><strong>Why:</strong> ${anomaly.summary_why_happened}</p>
            <p><strong>Impact:</strong> ${anomaly.summary_impact}</p>
            
            <button onclick="markFalsePositive('${anomaly.analysis_id}')">
                False Positive
            </button>
            <button onclick="markTruePositive('${anomaly.analysis_id}')">
                True Positive
            </button>
        `;
        document.getElementById('anomalies').appendChild(div);
    }
    
    async function markFalsePositive(analysisId) {
        const category = prompt('Why is this a false positive?', 'expected_behavior');
        const notes = prompt('Additional notes:');
        
        // Update BigQuery
        const query = `
            UPDATE \`ccibt-hack25ww7-730.hackaton.anomaly_analysis\`
            SET 
                is_false_positive = TRUE,
                reviewed_by = '${getCurrentUser()}',
                reviewed_at = CURRENT_TIMESTAMP(),
                review_notes = '${notes}',
                feedback_category = '${category}'
            WHERE analysis_id = '${analysisId}'
        `;
        
        await executeBigQueryUpdate(query);
        alert('Marked as false positive');
        loadAnomalies();  // Refresh
    }
    </script>
</body>
</html>
```

## Reporting and Dashboards

### Weekly Reliability Report

```sql
-- Generate weekly reliability report
SELECT 
    EXTRACT(WEEK FROM analyzed_at) as week_number,
    EXTRACT(YEAR FROM analyzed_at) as year,
    COUNT(*) as total_analyses,
    COUNTIF(is_false_positive = TRUE) as false_positives,
    COUNTIF(is_false_positive = FALSE) as true_positives,
    ROUND(SAFE_DIVIDE(COUNTIF(is_false_positive = TRUE), 
                      COUNTIF(is_false_positive IS NOT NULL)) * 100, 1) as fp_rate_pct,
    ROUND(AVG(root_cause_confidence) * 100, 1) as avg_confidence_pct
FROM `ccibt-hack25ww7-730.hackaton.anomaly_analysis`
WHERE analyzed_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 12 WEEK)
GROUP BY year, week_number
ORDER BY year DESC, week_number DESC;
```

### Improvement Tracking

```sql
-- Track improvement over time
WITH monthly_stats AS (
    SELECT 
        DATE_TRUNC(analyzed_at, MONTH) as month,
        SAFE_DIVIDE(COUNTIF(is_false_positive = TRUE), 
                    COUNTIF(is_false_positive IS NOT NULL)) as fp_rate
    FROM `ccibt-hack25ww7-730.hackaton.anomaly_analysis`
    WHERE analyzed_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 6 MONTH)
    GROUP BY month
)
SELECT 
    month,
    ROUND(fp_rate * 100, 1) as fp_rate_pct,
    ROUND((1 - fp_rate) * 100, 1) as reliability_pct,
    LAG(fp_rate) OVER (ORDER BY month) as prev_month_fp_rate,
    ROUND((fp_rate - LAG(fp_rate) OVER (ORDER BY month)) * 100, 1) as change_pct
FROM monthly_stats
ORDER BY month DESC;
```

## Best Practices

### 1. Regular Review Schedule
- Review unreviewed anomalies daily or weekly
- Prioritize critical and high severity anomalies
- Aim for 80%+ review rate

### 2. Consistent Categorization
- Use standard feedback categories
- Provide detailed review notes
- Be specific about why it's a false positive

### 3. Team Collaboration
- Multiple reviewers for critical anomalies
- Share insights from review notes
- Regular team discussions on patterns

### 4. Continuous Improvement
- Monitor false positive rate trends
- Adjust baselines based on feedback
- Update detection rules for common false positives
- Retrain AI models with feedback data

## Summary

The user feedback system:
- ✅ Tracks all anomaly analyses in BigQuery
- ✅ Allows users to mark false positives
- ✅ Calculates reliability metrics
- ✅ Identifies patterns in false positives
- ✅ Enables continuous improvement
- ✅ Provides transparency and accountability

**Goal**: Achieve and maintain 90%+ reliability score (10% or less false positive rate)

---

**Next Steps**:
1. Run `sql/create_anomaly_analysis_table.sql` to create the table
2. Start analyzing anomalies (they'll be saved automatically)
3. Review and mark false positives
4. Monitor reliability metrics
5. Use feedback to improve detection