#!/usr/bin/env python3
"""
Explore the hackaton dataset in BigQuery
"""

from google.cloud import bigquery
import json
from datetime import datetime

def explore_hackaton_dataset():
    """Explore the hackaton dataset"""
    
    client = bigquery.Client(project='ccibt-hack25ww7-730')
    dataset_id = 'hackaton'
    
    print("=" * 80)
    print("Exploring Dataset: hackaton")
    print("=" * 80)
    
    # List all tables
    print("\n1. Tables in Dataset:")
    print("-" * 80)
    
    try:
        tables = list(client.list_tables(dataset_id))
        
        if not tables:
            print("No tables found in dataset")
            return
        
        table_details = []
        
        for table in tables:
            table_ref = client.dataset(dataset_id).table(table.table_id)
            table_obj = client.get_table(table_ref)
            
            print(f"\nTable: {table.table_id}")
            print(f"  Rows: {table_obj.num_rows:,}")
            print(f"  Size: {table_obj.num_bytes / 1024 / 1024:.2f} MB")
            print(f"  Created: {table_obj.created}")
            print(f"  Modified: {table_obj.modified}")
            
            # Store details
            table_details.append({
                'table_name': table.table_id,
                'rows': table_obj.num_rows,
                'size_mb': round(table_obj.num_bytes / 1024 / 1024, 2),
                'created': str(table_obj.created),
                'modified': str(table_obj.modified)
            })
            
            # Print schema
            print(f"  Schema ({len(table_obj.schema)} columns):")
            for field in table_obj.schema:
                print(f"    - {field.name}: {field.field_type} ({field.mode})")
            
            # Sample data
            query = f"""
            SELECT *
            FROM `ccibt-hack25ww7-730.{dataset_id}.{table.table_id}`
            LIMIT 3
            """
            
            try:
                df = client.query(query).to_dataframe()
                print(f"\n  Sample Data (first 3 rows):")
                print(df.to_string(index=False))
            except Exception as e:
                print(f"  Error sampling data: {e}")
            
            # Get row count and date range if timestamp exists
            try:
                stats_query = f"""
                SELECT 
                    COUNT(*) as total_rows,
                    MIN(timestamp) as earliest_date,
                    MAX(timestamp) as latest_date
                FROM `ccibt-hack25ww7-730.{dataset_id}.{table.table_id}`
                """
                stats = client.query(stats_query).to_dataframe()
                print(f"\n  Statistics:")
                print(f"    Total Rows: {stats['total_rows'].iloc[0]:,}")
                if pd.notna(stats['earliest_date'].iloc[0]):
                    print(f"    Date Range: {stats['earliest_date'].iloc[0]} to {stats['latest_date'].iloc[0]}")
            except:
                pass
            
            print("\n" + "-" * 80)
        
        # Save summary
        summary = {
            'dataset': 'hackaton',
            'project': 'ccibt-hack25ww7-730',
            'explored_at': datetime.now().isoformat(),
            'table_count': len(tables),
            'tables': table_details
        }
        
        with open('hackaton_dataset_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "=" * 80)
        print(f"Found {len(tables)} table(s) in dataset 'hackaton'")
        print("Summary saved to: hackaton_dataset_summary.json")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error exploring dataset: {e}")

if __name__ == "__main__":
    import pandas as pd
    explore_hackaton_dataset()