#!/usr/bin/env python3
"""
Explore the existing BigQuery dataset
"""

from google.cloud import bigquery
import pandas as pd
from datetime import datetime
import json

def explore_dataset():
    """Explore the uc3-volume-spikes-analyzer dataset"""
    
    client = bigquery.Client(project='ccibt-hack25ww7-730')
    dataset_id = 'datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer'
    
    print("=" * 80)
    print("Exploring Dataset: uc3-volume-spikes-analyzer")
    print("=" * 80)
    
    # List all tables
    print("\n1. Tables in Dataset:")
    print("-" * 80)
    
    try:
        tables = list(client.list_tables(dataset_id))
    except Exception as e:
        print(f"Error listing tables: {e}")
        return
    
    if not tables:
        print("No tables found in dataset")
        return
    
    table_info = []
    
    for table in tables:
        try:
            table_ref = client.dataset(
                'uc3-volume-spikes-analyzer',
                project='datasets-ccibt-hack25ww7-730'
            ).table(table.table_id)
            
            table_obj = client.get_table(table_ref)
            
            info = {
                'table_name': table.table_id,
                'rows': table_obj.num_rows,
                'size_mb': table_obj.num_bytes / 1024 / 1024,
                'created': str(table_obj.created),
                'modified': str(table_obj.modified)
            }
            table_info.append(info)
            
            print(f"\nTable: {table.table_id}")
            print(f"  Rows: {table_obj.num_rows:,}")
            print(f"  Size: {table_obj.num_bytes / 1024 / 1024:.2f} MB")
            print(f"  Created: {table_obj.created}")
            print(f"  Modified: {table_obj.modified}")
            
            # Print schema
            print(f"  Schema:")
            for field in table_obj.schema:
                print(f"    - {field.name}: {field.field_type} ({field.mode})")
            
            # Sample data
            query = f"""
            SELECT *
            FROM `{dataset_id}.{table.table_id}`
            LIMIT 5
            """
            
            try:
                df = client.query(query).to_dataframe()
                print(f"\n  Sample Data (first 5 rows):")
                print(df.to_string(index=False))
            except Exception as e:
                print(f"  Error sampling data: {e}")
            
            print("\n" + "-" * 80)
        except Exception as e:
            print(f"Error processing table {table.table_id}: {e}")
    
    # Summary statistics
    print("\n2. Dataset Summary:")
    print("-" * 80)
    
    for table in tables:
        try:
            # Try to get date range if timestamp column exists
            query = f"""
            SELECT 
                '{table.table_id}' as table_name,
                COUNT(*) as row_count
            FROM `{dataset_id}.{table.table_id}`
            """
            
            result = client.query(query).to_dataframe()
            print(f"\n{table.table_id}:")
            print(f"  Total Rows: {result['row_count'].iloc[0]:,}")
            
            # Try to get date range
            try:
                date_query = f"""
                SELECT 
                    MIN(timestamp) as earliest,
                    MAX(timestamp) as latest,
                    TIMESTAMP_DIFF(MAX(timestamp), MIN(timestamp), DAY) as days_span
                FROM `{dataset_id}.{table.table_id}`
                """
                date_result = client.query(date_query).to_dataframe()
                print(f"  Date Range: {date_result['earliest'].iloc[0]} to {date_result['latest'].iloc[0]}")
                print(f"  Days Span: {date_result['days_span'].iloc[0]}")
            except:
                pass  # No timestamp column
                
        except Exception as e:
            print(f"  Error getting summary: {e}")
    
    # Save summary to JSON
    summary = {
        'dataset': 'uc3-volume-spikes-analyzer',
        'explored_at': datetime.now().isoformat(),
        'tables': table_info
    }
    
    with open('data_exploration_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 80)
    print("Summary saved to: data_exploration_summary.json")
    print("=" * 80)

if __name__ == "__main__":
    explore_dataset()