"""
Test Analysis Agent Locally
Tests anomaly analysis with sample data
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Use gcloud application default credentials
if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
    del os.environ['GOOGLE_APPLICATION_CREDENTIALS']

# Prevent dotenv from loading
os.environ['SKIP_DOTENV'] = '1'

# Add analysis-agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'analysis-agent'))

from src.agent.anomaly_analyzer import AnomalyAnalyzerAgent
from src.models.anomaly import Anomaly, AnomalyType, Severity
from src.utils.config import get_config

def test_analysis():
    """Test anomaly analysis with sample data"""
    
    print("=" * 80)
    print("ANALYSIS AGENT - LOCAL TEST")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Initialize analyzer
    print("Initializing analyzer...")
    config = get_config()
    analyzer = AnomalyAnalyzerAgent(config)
    
    print(f"Project: {config.bigquery_project_id}")
    print(f"Dataset: {config.bigquery_dataset_id}")
    print(f"AI Model: {config.insight_model}")
    print()
    
    # Create sample anomalies based on actual baseline data
    test_anomalies = [
        {
            'name': 'High Error Rate',
            'anomaly': Anomaly(
                anomaly_id='test-error-rate-001',
                detected_at=datetime.now(),
                metric_name='error_rate',
                metric_type='error_rate',
                current_value=8.5,  # Much higher than baseline mean of 2.52
                baseline_value=2.52,
                deviation_sigma=4.12,  # (8.5 - 2.52) / 1.45
                deviation_percentage=237.3,  # ((8.5 - 2.52) / 2.52) * 100
                anomaly_type=AnomalyType.STABILITY,
                severity=Severity.HIGH,
                confidence=0.95,
                affected_resources=[],
                time_window={},
                related_metrics={},
                metadata={'test': True}
            )
        },
        {
            'name': 'CPU Spike',
            'anomaly': Anomaly(
                anomaly_id='test-cpu-spike-001',
                detected_at=datetime.now(),
                metric_name='cpu_utilization',
                metric_type='cpu_utilization',
                current_value=95.0,  # Higher than baseline mean of 49.75
                baseline_value=49.75,
                deviation_sigma=1.95,  # (95 - 49.75) / 23.17
                deviation_percentage=90.9,  # ((95 - 49.75) / 49.75) * 100
                anomaly_type=AnomalyType.RESOURCE,
                severity=Severity.MEDIUM,
                confidence=0.85,
                affected_resources=[],
                time_window={},
                related_metrics={},
                metadata={'test': True}
            )
        },
        {
            'name': 'Memory Consumption Spike',
            'anomaly': Anomaly(
                anomaly_id='test-memory-spike-001',
                detected_at=datetime.now(),
                metric_name='memory_consumption',
                metric_type='memory_consumption',
                current_value=9500.0,  # Higher than baseline mean of 4218 MB
                baseline_value=4218.14,
                deviation_sigma=2.46,  # (9500 - 4218) / 2142
                deviation_percentage=125.2,  # ((9500 - 4218) / 4218) * 100
                anomaly_type=AnomalyType.RESOURCE,
                severity=Severity.HIGH,
                confidence=0.90,
                affected_resources=[],
                time_window={},
                related_metrics={},
                metadata={'test': True}
            )
        }
    ]
    
    results = []
    
    # Analyze each anomaly
    for test_case in test_anomalies:
        print("-" * 80)
        print(f"Testing: {test_case['name']}")
        print(f"Anomaly ID: {test_case['anomaly'].anomaly_id}")
        print(f"Metric: {test_case['anomaly'].metric_name}")
        print(f"Current Value: {test_case['anomaly'].current_value:.2f}")
        print(f"Baseline Value: {test_case['anomaly'].baseline_value:.2f}")
        print(f"Deviation: {test_case['anomaly'].deviation_sigma:.2f} sigma")
        print()
        
        try:
            # Analyze anomaly
            analysis = analyzer.analyze_anomaly(test_case['anomaly'])
            
            # Prepare result
            result = {
                'test_name': test_case['name'],
                'anomaly_id': analysis.anomaly.anomaly_id,
                'metric_name': analysis.anomaly.metric_name,
                'root_cause': {
                    'primary_cause': analysis.root_cause.primary_cause,
                    'contributing_factors': analysis.root_cause.contributing_factors,
                    'confidence': analysis.root_cause.confidence,
                    'evidence': analysis.root_cause.evidence
                },
                'recommendations': [
                    {
                        'priority': rec.priority,
                        'action': rec.action,
                        'rationale': rec.rationale,
                        'expected_impact': rec.expected_impact
                    }
                    for rec in analysis.recommendations
                ],
                'summary': {
                    'what_happened': analysis.summary.what_happened if analysis.summary else None,
                    'why_it_happened': analysis.summary.why_it_happened if analysis.summary else None,
                    'impact': analysis.summary.what_is_the_impact if analysis.summary else None,
                    'improvements': analysis.summary.what_improvements_can_be_made if analysis.summary else None,
                    'benefits': analysis.summary.estimated_benefit_if_implemented if analysis.summary else None
                },
                'analysis_duration_ms': analysis.analysis_duration_ms,
                'ai_model_used': analysis.ai_model_used
            }
            
            results.append(result)
            
            # Print summary
            print("[SUCCESS]")
            print(f"   Root Cause: {analysis.root_cause.primary_cause}")
            print(f"   Confidence: {analysis.root_cause.confidence:.0%}")
            print(f"   Recommendations: {len(analysis.recommendations)}")
            print(f"   Analysis Time: {analysis.analysis_duration_ms}ms")
            print(f"   AI Model: {analysis.ai_model_used}")
            
            if analysis.summary:
                print()
                print("   SUMMARY:")
                print(f"   What Happened: {analysis.summary.what_happened[:100]}...")
                print(f"   Why: {analysis.summary.why_it_happened[:100]}...")
            
            print()
            
        except Exception as e:
            print(f"[FAILED]: {str(e)}")
            print()
            import traceback
            traceback.print_exc()
            results.append({
                'test_name': test_case['name'],
                'error': str(e),
                'status': 'failed'
            })
    
    # Save results to file
    output_file = f"analysis_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    output_data = {
        'test_timestamp': datetime.now().isoformat(),
        'project_id': config.bigquery_project_id,
        'dataset_id': config.bigquery_dataset_id,
        'ai_model': config.insight_model,
        'total_tests': len(test_anomalies),
        'successful': len([r for r in results if 'error' not in r]),
        'failed': len([r for r in results if 'error' in r]),
        'results': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print(f"Total Tests: {len(test_anomalies)}")
    print(f"Successful: {output_data['successful']}")
    print(f"Failed: {output_data['failed']}")
    print(f"Results saved to: {output_file}")
    print()
    
    return output_data

if __name__ == "__main__":
    try:
        results = test_analysis()
        sys.exit(0 if results['failed'] == 0 else 1)
    except Exception as e:
        print(f"\n[TEST FAILED]: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)