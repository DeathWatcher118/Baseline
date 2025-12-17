"""
Compare Baseline Test Results
Reads all baseline test result files and creates a comparison report
"""

import json
import os
from datetime import datetime
from pathlib import Path

def load_test_results():
    """Load all baseline test result files"""
    results = []
    
    # Find all baseline test result files
    for file in Path('.').glob('baseline_test_results*.json'):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                data['filename'] = file.name
                results.append(data)
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    # Sort by timestamp
    results.sort(key=lambda x: x.get('test_timestamp', ''))
    
    return results

def format_comparison_report(results):
    """Create a formatted comparison report"""
    
    report = []
    report.append("=" * 120)
    report.append("BASELINE TEST RESULTS COMPARISON")
    report.append("=" * 120)
    report.append("")
    
    # Summary table
    report.append("TEST RUN SUMMARY")
    report.append("-" * 120)
    report.append(f"{'Run #':<8} {'Timestamp':<25} {'Method':<15} {'Lookback':<10} {'Saved to BQ':<12} {'Success':<10} {'File':<30}")
    report.append("-" * 120)
    
    for idx, result in enumerate(results, 1):
        timestamp = result.get('test_timestamp', 'N/A')[:19]
        method = result.get('calculation_method', 'N/A')
        lookback = f"{result.get('lookback_days', 'N/A')} days"
        saved_bq = 'YES' if result.get('saved_to_bigquery', True) else 'NO'
        success = f"{result.get('successful', 0)}/{result.get('total_metrics', 0)}"
        filename = result.get('filename', 'N/A')
        
        report.append(f"{idx:<8} {timestamp:<25} {method:<15} {lookback:<10} {saved_bq:<12} {success:<10} {filename:<30}")
    
    report.append("")
    report.append("")
    
    # Detailed comparison by metric
    report.append("DETAILED METRIC COMPARISON")
    report.append("=" * 120)
    
    # Get all unique metrics
    all_metrics = set()
    for result in results:
        for metric_result in result.get('results', []):
            if 'metric_name' in metric_result:
                all_metrics.add(metric_result['metric_name'])
    
    for metric_name in sorted(all_metrics):
        report.append("")
        report.append(f"METRIC: {metric_name.upper()}")
        report.append("-" * 120)
        report.append(f"{'Run #':<8} {'Timestamp':<20} {'Mean':<12} {'Std Dev':<12} {'Min':<10} {'Max':<10} {'P50':<10} {'P95':<10} {'P99':<10} {'Samples':<10}")
        report.append("-" * 120)
        
        for idx, result in enumerate(results, 1):
            # Find this metric in the results
            metric_data = None
            for metric_result in result.get('results', []):
                if metric_result.get('metric_name') == metric_name:
                    metric_data = metric_result
                    break
            
            if metric_data and 'statistics' in metric_data:
                stats = metric_data['statistics']
                timestamp = result.get('test_timestamp', 'N/A')[11:19]  # Just time
                mean = f"{stats.get('mean', 0):.2f}"
                std_dev = f"{stats.get('std_dev', 0):.2f}"
                min_val = f"{stats.get('min_value', 0):.2f}"
                max_val = f"{stats.get('max_value', 0):.2f}"
                p50 = f"{stats.get('p50', 0):.2f}"
                p95 = f"{stats.get('p95', 0):.2f}"
                p99 = f"{stats.get('p99', 0):.2f}"
                samples = f"{metric_data.get('metadata', {}).get('sample_count', 0):,}"
                
                report.append(f"{idx:<8} {timestamp:<20} {mean:<12} {std_dev:<12} {min_val:<10} {max_val:<10} {p50:<10} {p95:<10} {p99:<10} {samples:<10}")
            else:
                report.append(f"{idx:<8} {'N/A':<20} {'N/A':<12} {'N/A':<12} {'N/A':<10} {'N/A':<10} {'N/A':<10} {'N/A':<10} {'N/A':<10} {'N/A':<10}")
        
        # Calculate variance between runs
        values = []
        for result in results:
            for metric_result in result.get('results', []):
                if metric_result.get('metric_name') == metric_name and 'statistics' in metric_result:
                    values.append(metric_result['statistics'].get('mean', 0))
        
        if len(values) > 1:
            max_diff = max(values) - min(values)
            avg_val = sum(values) / len(values)
            variance_pct = (max_diff / avg_val * 100) if avg_val > 0 else 0
            report.append("-" * 120)
            report.append(f"Variance: Max Diff = {max_diff:.4f}, Avg = {avg_val:.4f}, Variance = {variance_pct:.2f}%")
    
    report.append("")
    report.append("=" * 120)
    report.append("END OF COMPARISON REPORT")
    report.append("=" * 120)
    
    return "\n".join(report)

def create_csv_comparison(results):
    """Create CSV format for easy import to Excel"""
    
    csv_lines = []
    csv_lines.append("Run,Timestamp,Metric,Mean,StdDev,Min,Max,P50,P95,P99,Samples,SavedToBQ")
    
    for idx, result in enumerate(results, 1):
        timestamp = result.get('test_timestamp', 'N/A')
        saved_bq = 'YES' if result.get('saved_to_bigquery', True) else 'NO'
        
        for metric_result in result.get('results', []):
            if 'statistics' in metric_result:
                metric_name = metric_result.get('metric_name', 'unknown')
                stats = metric_result['statistics']
                samples = metric_result.get('metadata', {}).get('sample_count', 0)
                
                csv_lines.append(
                    f"{idx},{timestamp},{metric_name},"
                    f"{stats.get('mean', 0):.4f},"
                    f"{stats.get('std_dev', 0):.4f},"
                    f"{stats.get('min_value', 0):.4f},"
                    f"{stats.get('max_value', 0):.4f},"
                    f"{stats.get('p50', 0):.4f},"
                    f"{stats.get('p95', 0):.4f},"
                    f"{stats.get('p99', 0):.4f},"
                    f"{samples},{saved_bq}"
                )
    
    return "\n".join(csv_lines)

if __name__ == "__main__":
    print("Loading baseline test results...")
    results = load_test_results()
    
    if not results:
        print("No baseline test result files found!")
        exit(1)
    
    print(f"Found {len(results)} test result files")
    print()
    
    # Create comparison report
    report = format_comparison_report(results)
    
    # Save to file
    report_file = f"baseline_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(report)
    print()
    print(f"Report saved to: {report_file}")
    
    # Create CSV
    csv_data = create_csv_comparison(results)
    csv_file = f"baseline_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(csv_file, 'w') as f:
        f.write(csv_data)
    
    print(f"CSV data saved to: {csv_file}")