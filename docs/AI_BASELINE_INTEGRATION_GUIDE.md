# AI-Driven Baseline Calculation Integration Guide

## Overview

This guide explains how to enable AI-driven baseline calculation using Vertex AI and ADK (Agent Development Kit) to automatically determine the optimal baseline calculation method for each metric.

## Current State vs. AI-Enhanced State

### Current Implementation (Rule-Based)
```python
# src/baseline/ai_optimizer.py - Line 248
def _rule_based_recommendation(self, characteristics):
    """Simple rule-based logic"""
    if volatility == "high":
        method = "rolling_average"
    elif trend != "stable":
        method = "rolling_average"
    else:
        method = "simple_stats"
    return recommendation
```

### AI-Enhanced Implementation (Gemini-Powered)
```python
# Uses Vertex AI Gemini to analyze data and recommend method
def _get_ai_recommendation(self, characteristics):
    """AI analyzes data and recommends optimal method"""
    response = gemini_model.generate_content(prompt)
    return parse_ai_response(response)
```

## What's Needed to Enable AI

### 1. Vertex AI Setup (GCP Console)

#### Enable APIs
```bash
# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable generativelanguage.googleapis.com
```

#### Create Service Account
```bash
# Create service account for Vertex AI
gcloud iam service-accounts create baseline-ai-optimizer \
    --display-name="Baseline AI Optimizer"

# Grant permissions
gcloud projects add-iam-policy-binding ccibt-hack25ww7-730 \
    --member="serviceAccount:baseline-ai-optimizer@ccibt-hack25ww7-730.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create baseline-ai-key.json \
    --iam-account=baseline-ai-optimizer@ccibt-hack25ww7-730.iam.gserviceaccount.com
```

### 2. Code Changes Required

#### Update `src/baseline/ai_optimizer.py`

Replace the `_call_adk_api` method (currently a stub) with actual Vertex AI integration:

```python
def _call_adk_api(self, prompt: str) -> Dict[str, Any]:
    """
    Call Vertex AI Gemini API for recommendation
    """
    import vertexai
    from vertexai.generative_models import GenerativeModel
    
    # Initialize Vertex AI
    vertexai.init(
        project=self.config.bigquery_project_id,
        location=self.config.get('bigquery.location', 'us-central1')
    )
    
    # Create model instance
    model = GenerativeModel(self.config.insight_model)
    
    # Generate response
    response = model.generate_content(
        prompt,
        generation_config={
            'temperature': self.config.insight_temperature,
            'max_output_tokens': self.config.insight_max_tokens,
        }
    )
    
    # Parse JSON response
    try:
        result = json.loads(response.text)
        logger.info(f"AI recommendation received: {result['recommended_method']}")
        return result
    except json.JSONDecodeError:
        logger.warning("Failed to parse AI response, using rule-based fallback")
        return self._rule_based_recommendation({})
```

#### Update `src/baseline/calculator.py`

Add AI-driven method selection:

```python
def calculate_baseline_with_ai(
    self,
    metric_name: str,
    metric_column: str,
    source_table: str
) -> BaselineStats:
    """
    Calculate baseline using AI-recommended method
    """
    from ..baseline.ai_optimizer import AIBaselineOptimizer
    
    logger.info(f"Using AI to determine optimal method for {metric_name}")
    
    # Get sample data for analysis
    query = f"""
    SELECT `{metric_column}` as value
    FROM `{self.project_id}.{self.dataset_id}.{source_table}`
    WHERE `{metric_column}` IS NOT NULL
    LIMIT 10000
    """
    
    df = self.client.query(query).to_dataframe()
    
    # Get AI recommendation
    optimizer = AIBaselineOptimizer(self.config)
    recommendation = optimizer.analyze_metric(
        metric_name=metric_name,
        data=df['value']
    )
    
    logger.info(f"AI recommends: {recommendation['recommended_method']} "
                f"(confidence: {recommendation['confidence']:.0%})")
    
    # Use recommended method
    return self.calculate_baseline(
        metric_name=metric_name,
        metric_column=metric_column,
        source_table=source_table,
        calculation_method=recommendation['recommended_method'],
        lookback_days=recommendation['parameters']['lookback_days']
    )
```

### 3. Configuration Updates

#### Update `config.yaml`

```yaml
# Enable AI-driven baseline optimization
baseline:
  use_ai_optimization: true  # NEW: Enable AI recommendations
  ai_confidence_threshold: 0.75  # NEW: Minimum confidence to use AI recommendation
  fallback_to_rules: true  # NEW: Use rule-based if AI fails
  
  # Existing settings...
  lookback_days: 30
  calculation_method: "simple_stats"  # Used as fallback

# Vertex AI settings
vertex_ai:
  project_id: "ccibt-hack25ww7-730"
  location: "us-central1"
  model: "gemini-1.5-pro"
  
insight:
  model: "gemini-1.5-pro"
  max_tokens: 1024
  temperature: 0.3
```

### 4. Environment Variables

#### Update `.env`

```env
# Existing
GCP_PROJECT_ID=ccibt-hack25ww7-730
GCP_REGION=us-central1

# NEW: Vertex AI credentials
GOOGLE_APPLICATION_CREDENTIALS=path/to/baseline-ai-key.json
VERTEX_AI_LOCATION=us-central1

# Optional: Direct Gemini API (alternative to Vertex AI)
GEMINI_API_KEY=your-gemini-api-key-here
```

### 5. Additional Dependencies

#### Update `requirements.txt`

```txt
# Existing packages...
google-cloud-bigquery>=3.11.0
google-cloud-aiplatform>=1.38.0

# NEW: For AI integration
vertexai>=1.38.0
google-generativeai>=0.3.0  # Alternative: Direct Gemini API
```

Install new dependencies:
```bash
pip install --upgrade vertexai google-generativeai
```

## Implementation Steps

### Step 1: Enable Vertex AI (5 minutes)

```bash
# Run these commands
gcloud services enable aiplatform.googleapis.com
gcloud auth application-default login
```

### Step 2: Update Code (15 minutes)

1. Replace `_call_adk_api` stub in `ai_optimizer.py`
2. Add `calculate_baseline_with_ai` method to `calculator.py`
3. Update configuration loading in `config.py`

### Step 3: Test AI Integration (10 minutes)

```python
# Test script: scripts/test_ai_baseline.py
from src.baseline.ai_optimizer import AIBaselineOptimizer
import pandas as pd
import numpy as np

# Create test data
data = pd.Series(np.random.normal(50, 10, 1000))

# Test AI recommendation
optimizer = AIBaselineOptimizer()
recommendation = optimizer.analyze_metric("test_metric", data)

print(f"AI Recommendation: {recommendation['recommended_method']}")
print(f"Confidence: {recommendation['confidence']:.0%}")
print(f"Reasoning: {recommendation['reasoning']}")
```

### Step 4: Deploy with AI Enabled (5 minutes)

```bash
# Deploy to Cloud Run with AI enabled
gcloud run deploy baseline-calculator \
  --image gcr.io/ccibt-hack25ww7-730/baseline-calculator:latest \
  --region us-central1 \
  --set-env-vars USE_AI_OPTIMIZATION=true \
  --set-env-vars VERTEX_AI_LOCATION=us-central1
```

## Usage Examples

### Example 1: Single Metric with AI

```python
from src.baseline.calculator import BaselineCalculator

calculator = BaselineCalculator()

# AI will analyze data and choose best method
baseline = calculator.calculate_baseline_with_ai(
    metric_name="error_rate",
    metric_column="Error_Rate _%_",
    source_table="cloud_workload_dataset"
)

print(f"Method used: {baseline.notes}")
print(f"Mean: {baseline.mean:.4f}")
```

### Example 2: Batch Processing with AI

```python
from src.baseline.calculator import BaselineCalculator

calculator = BaselineCalculator()

metrics = [
    {"name": "error_rate", "column": "Error_Rate _%_"},
    {"name": "cpu_utilization", "column": "CPU_Utilization _%_"},
    {"name": "memory_consumption", "column": "Memory_Consumption _MB_"},
]

for metric in metrics:
    baseline = calculator.calculate_baseline_with_ai(
        metric_name=metric["name"],
        metric_column=metric["column"],
        source_table="cloud_workload_dataset"
    )
    print(f"{metric['name']}: {baseline.notes}")
```

### Example 3: Compare AI vs Rule-Based

```python
from src.baseline.ai_optimizer import AIBaselineOptimizer
import pandas as pd

optimizer = AIBaselineOptimizer()

# Get sample data
data = get_metric_data("error_rate")

# Get AI recommendation
ai_rec = optimizer.analyze_metric("error_rate", data)

# Get rule-based recommendation
rule_rec = optimizer._rule_based_recommendation(
    optimizer._analyze_data_characteristics(data)
)

print(f"AI recommends: {ai_rec['recommended_method']} ({ai_rec['confidence']:.0%})")
print(f"Rules recommend: {rule_rec['recommended_method']} ({rule_rec['confidence']:.0%})")
```

## Cost Considerations

### Vertex AI Pricing (Gemini 1.5 Pro)

- **Input**: $0.00125 per 1K characters
- **Output**: $0.00375 per 1K characters

### Estimated Costs

**Per Baseline Calculation:**
- Prompt: ~2K characters = $0.0025
- Response: ~500 characters = $0.0019
- **Total per metric: ~$0.0044**

**Daily Baseline Refresh (4 metrics):**
- 4 metrics × $0.0044 = **$0.0176/day**
- **Monthly: ~$0.53**

**Very cost-effective for the value provided!**

## Benefits of AI-Driven Baseline

### 1. Adaptive Method Selection
- AI analyzes actual data patterns
- Chooses optimal method for each metric
- Adapts to changing data characteristics

### 2. Improved Accuracy
- Better anomaly detection
- Fewer false positives
- More relevant baselines

### 3. Explainability
- AI provides reasoning for recommendations
- Confidence scores for transparency
- Alternative methods suggested

### 4. Continuous Learning
- Can be retrained on historical performance
- Learns from feedback
- Improves over time

## Monitoring AI Performance

### Track AI Recommendations

```python
# Log AI decisions for analysis
logger.info(f"AI Recommendation Log", extra={
    'metric': metric_name,
    'recommended_method': recommendation['recommended_method'],
    'confidence': recommendation['confidence'],
    'reasoning': recommendation['reasoning'],
    'data_characteristics': characteristics
})
```

### Compare AI vs Manual

```sql
-- Query to compare AI vs manual baseline accuracy
SELECT 
  metric_name,
  calculation_method,
  AVG(anomaly_detection_accuracy) as avg_accuracy
FROM baseline_performance
GROUP BY metric_name, calculation_method
ORDER BY avg_accuracy DESC
```

## Fallback Strategy

The system is designed with robust fallbacks:

1. **Primary**: AI recommendation (Vertex AI/Gemini)
2. **Fallback 1**: Rule-based recommendation
3. **Fallback 2**: Default method from config
4. **Fallback 3**: Simple stats (always works)

```python
def get_calculation_method(self, metric_name, data):
    """Get method with fallback chain"""
    try:
        # Try AI first
        return self._get_ai_recommendation(metric_name, data)
    except Exception as e:
        logger.warning(f"AI failed: {e}, using rules")
        try:
            # Try rule-based
            return self._rule_based_recommendation(data)
        except Exception as e:
            logger.warning(f"Rules failed: {e}, using default")
            # Use config default
            return self.config.baseline_calculation_method
```

## Summary: What's Needed

### ✅ Already Have
- AI optimizer structure (`ai_optimizer.py`)
- Configuration system
- Data analysis functions
- Rule-based fallback

### 🔧 Need to Add
1. **Vertex AI Integration** (30 min)
   - Enable APIs
   - Create service account
   - Update `_call_adk_api` method

2. **Configuration Updates** (5 min)
   - Add AI settings to `config.yaml`
   - Update `.env` with credentials

3. **Testing** (15 min)
   - Test AI recommendations
   - Verify fallback chain
   - Compare AI vs rules

### 📊 Total Time to Enable AI
**~50 minutes** to go from current rule-based to full AI-driven baseline calculation

### 💰 Total Cost
**~$0.53/month** for daily baseline calculations (4 metrics)

---

**Ready to enable AI?** Follow the steps above and your baseline calculator will use Gemini to intelligently choose the best calculation method for each metric!