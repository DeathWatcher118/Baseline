"""
Test Baseline Calculator Locally - WITHOUT saving to BigQuery
Calculates baselines from BigQuery data and saves results ONLY locally
"""

import os
import sys
import json
from datetime import datetime

# Use gcloud application default credentials instead of service account key
# Remove any .env file credentials
if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
    del os.environ['GOOGLE_APPLICATION_CREDENTIALS']

# Prevent dotenv from loading
os.environ['SKIP_DOTENV'] = '1'

# Add baseline-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'baseline-service'))

from src.baseline.calculator import BaselineCalculator
from src.utils.config import get_config

def test_baseline_calculation():
    """Test baseline calculation for all metrics - LOCAL ONLY"""
    
    print("=" * 80)
    print("BASELINE CALCULATOR - LOCAL TEST (NO BIGQUERY SAVE)")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Initialize calculator
    print("Initializing calculator...")
    config = get_config()
    calculator = BaselineCalculator(config)
    
    print(f"Project: {calculator.project_id}")
    print(f"Dataset: {calculator.dataset_id}")
    print(f"Method: {calculator.calculation_method}")
    print(f"Lookback: {calculator.lookback_days} days")
    print()
    
    # Metrics to test (using actual BigQuery column names)
    metrics = [
        {
            'name': 'error_rate',
            'column': 'Error_Rate _percentage_',
            'table': 'cloud_workload_dataset'
        },
        {
            'name': 'cpu_utilization',
            'column': 'CPU_Utilization_percentage_',
            'table': 'cloud_workload_dataset'
        },
        {
            'name': 'memory_consumption',
            'column': 'Memory_Consumption_MB_',
            'table': 'cloud_workload_dataset'
        },
        {
            'name': 'execution_time',
            'column': 'Task_Execution_Time _ms_',
            'table': 'cloud_workload_dataset'
        }
    ]
    
    results = []
    
    # Calculate baselines
    for metric in metrics:
        print("-" * 80)
        print(f"Processing: {metric['name']}")
        print(f"Column: {metric['column']}")
        print(f"Table: {metric['table']}")
        print()
        
        try:
            # Calculate baseline (NO SAVE TO BIGQUERY)
            baseline = calculator.calculate_baseline(
                metric_name=metric['name'],
                metric_column=metric['column'],
                source_table=metric['table']
            )
            
            # DO NOT SAVE TO BIGQUERY - only save locally
            # calculator.save_baseline(baseline)  # COMMENTED OUT
            
            # Prepare result
            result = {
                'baseline_id': baseline.baseline_id,
                'metric_name': baseline.metric_name,
                'statistics': {
                    'mean': baseline.mean,
                    'std_dev': baseline.std_dev,
                    'min_value': baseline.min_value,
                    'max_value': baseline.max_value,
                    'p50': baseline.p50,
                    'p95': baseline.p95,
                    'p99': baseline.p99
                },
                'metadata': {
                    'calculated_at': baseline.calculated_at.isoformat(),
                    'lookback_days': baseline.lookback_days,
                    'sample_count': baseline.sample_count,
                    'data_source': baseline.data_source,
                    'notes': baseline.notes
                }
            }
            
            results.append(result)
            
            # Print summary
            print(f"[SUCCESS]")
            print(f"   Baseline ID: {baseline.baseline_id}")
            print(f"   Mean: {baseline.mean:.4f}")
            print(f"   Std Dev: {baseline.std_dev:.4f}")
            print(f"   P50: {baseline.p50:.4f}")
            print(f"   P95: {baseline.p95:.4f}")
            print(f"   P99: {baseline.p99:.4f}")
            print(f"   Samples: {baseline.sample_count:,}")
            print(f"   Saved to BigQuery: NO (local only)")
            print()
            
        except Exception as e:
            print(f"[FAILED]: {str(e)}")
            print()
            results.append({
                'metric_name': metric['name'],
                'error': str(e),
                'status': 'failed'
            })
    
    # Save results to file
    output_file = f"baseline_test_results_local_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    output_data = {
        'test_timestamp': datetime.now().isoformat(),
        'project_id': calculator.project_id,
        'dataset_id': calculator.dataset_id,
        'calculation_method': calculator.calculation_method,
        'lookback_days': calculator.lookback_days,
        'saved_to_bigquery': False,
        'note': 'This is a local test only - data NOT saved to BigQuery',
        'total_metrics': len(metrics),
        'successful': len([r for r in results if 'error' not in r]),
        'failed': len([r for r in results if 'error' in r]),
        'results': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print(f"Total Metrics: {len(metrics)}")
    print(f"Successful: {output_data['successful']}")
    print(f"Failed: {output_data['failed']}")
    print(f"Saved to BigQuery: NO")
    print(f"Results saved locally to: {output_file}")
    print()
    
    return output_data

if __name__ == "__main__":
    try:
        results = test_baseline_calculation()
        sys.exit(0 if results['failed'] == 0 else 1)
    except Exception as e:
        print(f"\n[TEST FAILED]: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)