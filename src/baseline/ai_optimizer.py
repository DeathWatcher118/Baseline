"""
AI-Driven Baseline Optimizer
Uses Vertex AI Gemini to analyze data and recommend optimal baseline calculation methods
"""

import json
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

from ..utils.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIBaselineOptimizer:
    """
    Uses AI to analyze time series data and recommend optimal baseline methods
    
    Analyzes:
    - Data distribution
    - Trend patterns
    - Seasonality
    - Volatility
    - Sample size
    
    Recommends:
    - Best calculation method
    - Optimal parameters
    - Confidence score
    - Reasoning
    """
    
    def __init__(self, config=None):
        """
        Initialize AI optimizer
        
        Args:
            config: Config object. If None, uses global config.
        """
        self.config = config or get_config()
        self.use_ai = self.config.get('baseline.use_ai_optimization', False)
        self.ai_confidence_threshold = self.config.get('baseline.ai_confidence_threshold', 0.75)
        
        # Initialize Vertex AI
        try:
            vertexai.init(
                project=self.config.bigquery_project_id,
                location=self.config.get('bigquery.location', 'us-central1')
            )
            self.ai_available = True
            logger.info("AI Baseline Optimizer initialized with Vertex AI")
            logger.info(f"Model: {self.config.insight_model}")
            logger.info(f"AI Optimization: {'ENABLED' if self.use_ai else 'DISABLED'}")
        except Exception as e:
            self.ai_available = False
            logger.warning(f"Vertex AI initialization failed: {e}")
            logger.info("Falling back to rule-based recommendations")
    
    def analyze_metric(
        self,
        metric_name: str,
        data: pd.Series,
        current_method: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze metric data and recommend optimal baseline method
        
        Args:
            metric_name: Name of the metric
            data: Time series data (pandas Series)
            current_method: Current calculation method (if any)
        
        Returns:
            Dictionary with recommendation:
            {
                'recommended_method': str,
                'confidence': float,
                'reasoning': str,
                'parameters': dict,
                'data_characteristics': dict
            }
        """
        logger.info(f"Analyzing {metric_name} for optimal baseline method")
        
        # Analyze data characteristics
        characteristics = self._analyze_data_characteristics(data)
        
        logger.info(f"Data characteristics for {metric_name}:")
        logger.info(f"  Samples: {characteristics['sample_count']:,}")
        logger.info(f"  Trend: {characteristics['trend']}")
        logger.info(f"  Seasonality: {characteristics['seasonality']}")
        logger.info(f"  Volatility: {characteristics['volatility']}")
        logger.info(f"  Distribution: {characteristics['distribution']}")
        
        # Get AI recommendation (if enabled and available)
        if self.use_ai and self.ai_available:
            try:
                recommendation = self._get_ai_recommendation(
                    metric_name,
                    characteristics,
                    current_method
                )
                
                # Check confidence threshold
                if recommendation['confidence'] >= self.ai_confidence_threshold:
                    logger.info(f"AI Recommendation for {metric_name}:")
                    logger.info(f"  Method: {recommendation['recommended_method']}")
                    logger.info(f"  Confidence: {recommendation['confidence']:.0%}")
                    logger.info(f"  Reasoning: {recommendation['reasoning'][:100]}...")
                    return recommendation
                else:
                    logger.warning(f"AI confidence ({recommendation['confidence']:.0%}) below threshold ({self.ai_confidence_threshold:.0%})")
                    logger.info("Falling back to rule-based recommendation")
            except Exception as e:
                logger.error(f"AI recommendation failed: {e}")
                logger.info("Falling back to rule-based recommendation")
        
        # Use rule-based recommendation
        recommendation = self._rule_based_recommendation(characteristics)
        logger.info(f"Rule-based recommendation for {metric_name}:")
        logger.info(f"  Method: {recommendation['recommended_method']}")
        logger.info(f"  Confidence: {recommendation['confidence']:.0%}")
        
        return recommendation
    
    def _analyze_data_characteristics(self, data: pd.Series) -> Dict[str, Any]:
        """
        Analyze statistical characteristics of the data
        """
        # Basic statistics
        mean = float(data.mean())
        std_dev = float(data.std())
        cv = std_dev / mean if mean != 0 else 0  # Coefficient of variation
        
        # Trend analysis (simple linear regression)
        x = np.arange(len(data))
        z = np.polyfit(x, data, 1)
        trend_slope = z[0]
        
        if abs(trend_slope) < 0.01 * mean:
            trend = "stable"
        elif trend_slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        # Seasonality detection (simplified - check for periodic patterns)
        # For MVP, we'll use a simple heuristic
        # In production, use proper time series decomposition
        seasonality = "unknown"  # Simplified for MVP
        
        # Volatility assessment
        if cv < 0.1:
            volatility = "low"
        elif cv < 0.3:
            volatility = "medium"
        else:
            volatility = "high"
        
        # Distribution analysis
        skewness = float(data.skew())
        if abs(skewness) < 0.5:
            distribution = "normal"
        elif skewness > 0:
            distribution = "right_skewed"
        else:
            distribution = "left_skewed"
        
        return {
            'sample_count': len(data),
            'mean': mean,
            'std_dev': std_dev,
            'coefficient_of_variation': cv,
            'trend': trend,
            'trend_slope': float(trend_slope),
            'seasonality': seasonality,
            'volatility': volatility,
            'distribution': distribution,
            'skewness': skewness,
            'min': float(data.min()),
            'max': float(data.max()),
            'range': float(data.max() - data.min())
        }
    
    def _get_ai_recommendation(
        self,
        metric_name: str,
        characteristics: Dict[str, Any],
        current_method: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use ADK/Gemini to recommend optimal baseline method
        """
        
        # Prepare prompt for AI
        prompt = f"""
You are an expert in time series analysis and anomaly detection. Analyze the following metric data and recommend the best baseline calculation method.

METRIC: {metric_name}

DATA CHARACTERISTICS:
- Sample Count: {characteristics['sample_count']:,}
- Mean: {characteristics['mean']:.2f}
- Standard Deviation: {characteristics['std_dev']:.2f}
- Coefficient of Variation: {characteristics['coefficient_of_variation']:.2f}
- Trend: {characteristics['trend']} (slope: {characteristics['trend_slope']:.4f})
- Volatility: {characteristics['volatility']}
- Distribution: {characteristics['distribution']} (skewness: {characteristics['skewness']:.2f})
- Range: [{characteristics['min']:.2f}, {characteristics['max']:.2f}]

AVAILABLE BASELINE METHODS:

1. **simple_stats**: Basic statistical baseline (mean, std dev, percentiles)
   - Best for: Stable data with normal distribution
   - Pros: Fast, simple, reliable
   - Cons: Doesn't handle trends or seasonality
   - Lookback: 30-90 days

2. **rolling_average**: Time-based rolling window average
   - Best for: Data with gradual trends
   - Pros: Adapts to slow changes
   - Cons: Lags behind rapid changes
   - Lookback: 7-30 days

3. **seasonal_decomposition**: Separates trend, seasonal, and residual components
   - Best for: Data with clear seasonal patterns (daily, weekly, monthly)
   - Pros: Handles complex patterns
   - Cons: Requires more data, computationally expensive
   - Lookback: 60-180 days (multiple seasons)

CURRENT METHOD: {current_method or 'None'}

TASK:
Analyze the data characteristics and recommend the BEST baseline calculation method for this metric.

RESPOND IN JSON FORMAT:
{{
  "recommended_method": "simple_stats|rolling_average|seasonal_decomposition",
  "confidence": 0.85,
  "reasoning": "Detailed explanation of why this method is best for this data...",
  "parameters": {{
    "lookback_days": 30,
    "additional_params": {{}}
  }},
  "alternative_methods": [
    {{
      "method": "method_name",
      "confidence": 0.65,
      "reason": "Why this could also work..."
    }}
  ]
}}

IMPORTANT:
- Be specific and data-driven in your reasoning
- Consider the trade-offs between accuracy and computational cost
- Recommend parameters that balance performance and resource usage
"""

        # Try to use AI if available
        if self.ai_available:
            try:
                return self._call_vertex_ai(prompt, characteristics)
            except Exception as e:
                logger.warning(f"Vertex AI call failed: {e}, using rule-based fallback")
        
        # Fallback to rule-based
        return self._rule_based_recommendation(characteristics)
    
    def _rule_based_recommendation(
        self,
        characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Rule-based recommendation (fallback for MVP)
        Will be replaced with ADK API call in production
        """
        
        # Decision logic based on data characteristics
        volatility = characteristics['volatility']
        trend = characteristics['trend']
        sample_count = characteristics['sample_count']
        
        # Default to simple_stats
        method = "simple_stats"
        lookback_days = 30
        confidence = 0.75
        reasoning = "Data shows stable characteristics suitable for simple statistical baseline."
        
        # Adjust based on characteristics
        if volatility == "high":
            method = "rolling_average"
            lookback_days = 14
            confidence = 0.80
            reasoning = "High volatility detected. Rolling average will adapt better to rapid changes."
        
        elif trend != "stable":
            method = "rolling_average"
            lookback_days = 21
            confidence = 0.85
            reasoning = f"Data shows {trend} trend. Rolling average will track the trend better than static baseline."
        
        elif sample_count > 10000:
            # Enough data for more sophisticated methods
            method = "seasonal_decomposition"
            lookback_days = 90
            confidence = 0.70
            reasoning = "Large dataset available. Seasonal decomposition can capture complex patterns."
        
        return {
            'recommended_method': method,
            'confidence': confidence,
            'reasoning': reasoning,
            'parameters': {
                'lookback_days': lookback_days,
                'additional_params': {}
            },
            'alternative_methods': [
                {
                    'method': 'simple_stats',
                    'confidence': 0.65,
                    'reason': 'Fallback option - always reliable'
                }
            ],
            'data_characteristics': characteristics
        }
    
    def _call_vertex_ai(self, prompt: str, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call Vertex AI Gemini API for recommendation
        """
        try:
            logger.info("Calling Vertex AI Gemini for baseline recommendation")
            
            # Create Gemini model instance
            model = GenerativeModel(self.config.insight_model)
            
            # Configure generation
            generation_config = GenerationConfig(
                temperature=self.config.insight_temperature,
                max_output_tokens=self.config.insight_max_tokens,
            )
            
            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Handle markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif response_text.startswith('```'):
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            try:
                result = json.loads(response_text)
                
                logger.info(f"AI recommendation received: {result['recommended_method']}")
                logger.info(f"AI confidence: {result['confidence']:.0%}")
                
                # Add data characteristics to result
                result['data_characteristics'] = characteristics
                
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.debug(f"Response text: {response_text[:200]}...")
                raise
                
        except Exception as e:
            logger.error(f"Vertex AI API call failed: {e}")
            raise


if __name__ == "__main__":
    # Test AI optimizer
    print("=" * 80)
    print("AI BASELINE OPTIMIZER TEST")
    print("=" * 80)
    
    # Create sample data
    import pandas as pd
    import numpy as np
    
    # Stable data
    stable_data = pd.Series(np.random.normal(50, 10, 1000))
    
    # Trending data
    trending_data = pd.Series(np.arange(1000) * 0.1 + np.random.normal(0, 5, 1000))
    
    # Volatile data
    volatile_data = pd.Series(np.random.normal(50, 30, 1000))
    
    optimizer = AIBaselineOptimizer()
    
    # Test with different data types
    for name, data in [
        ("Stable Metric", stable_data),
        ("Trending Metric", trending_data),
        ("Volatile Metric", volatile_data)
    ]:
        print(f"\n{'=' * 80}")
        print(f"Testing: {name}")
        print('=' * 80)
        
        recommendation = optimizer.analyze_metric(name, data)
        
        print(f"\nRecommendation Summary:")
        print(f"  Method: {recommendation['recommended_method']}")
        print(f"  Confidence: {recommendation['confidence']:.0%}")
        print(f"  Lookback Days: {recommendation['parameters']['lookback_days']}")
        print(f"  Reasoning: {recommendation['reasoning']}")