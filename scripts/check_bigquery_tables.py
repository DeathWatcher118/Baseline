#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check BigQuery tables and schema
Verifies that required tables exist and shows their structure
"""

import os
import sys
from google.cloud import bigquery
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def check_bigquery_tables():
    """Check if BigQuery tables exist and show their schema"""
    
    # Initialize BigQuery client
    project_id = os.getenv('GCP_PROJECT_ID', 'ccibt-hack25ww7-730')
    
    try:
        client = bigquery.Client(project=project_id)
        print(f"[OK] Connected to project: {project_id}\n")
        
        # List all datasets
        print("=" * 80)
        print("DATASETS IN PROJECT")
        print("=" * 80)
        datasets = list(client.list_datasets())
        
        if not datasets:
            print("⚠️  No datasets found in project")
            return
        
        for dataset in datasets:
            print(f"\n[Dataset] {dataset.dataset_id}")
            
            # List tables in each dataset
            dataset_ref = client.dataset(dataset.dataset_id)
            tables = list(client.list_tables(dataset_ref))
            
            if not tables:
                print("   No tables found")
                continue
            
            for table in tables:
                print(f"\n   [Table] {table.table_id}")
                
                # Get table details
                table_ref = dataset_ref.table(table.table_id)
                table_obj = client.get_table(table_ref)
                
                print(f"      Rows: {table_obj.num_rows:,}")
                print(f"      Size: {table_obj.num_bytes / (1024*1024):.2f} MB")
                print(f"      Created: {table_obj.created}")
                
                # Show schema
                print(f"\n      Schema ({len(table_obj.schema)} columns):")
                for i, field in enumerate(table_obj.schema[:10], 1):  # Show first 10 columns
                    print(f"         {i}. {field.name} ({field.field_type})")
                
                if len(table_obj.schema) > 10:
                    print(f"         ... and {len(table_obj.schema) - 10} more columns")
                
                # Sample data
                print(f"\n      Sample data (first 3 rows):")
                query = f"""
                SELECT *
                FROM `{project_id}.{dataset.dataset_id}.{table.table_id}`
                LIMIT 3
                """
                
                try:
                    results = client.query(query).result()
                    for row in results:
                        print(f"         {dict(row)}")
                except Exception as e:
                    print(f"         Error querying table: {e}")
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total datasets: {len(datasets)}")
        total_tables = sum(len(list(client.list_tables(client.dataset(d.dataset_id)))) for d in datasets)
        print(f"Total tables: {total_tables}")
        
        # Check for expected tables
        print("\n" + "=" * 80)
        print("EXPECTED TABLES CHECK")
        print("=" * 80)
        
        expected_tables = [
            "borg_traces",
            "cloud_workload", 
            "migrations",
            "workload_metrics"
        ]
        
        found_tables = []
        for dataset in datasets:
            dataset_ref = client.dataset(dataset.dataset_id)
            tables = list(client.list_tables(dataset_ref))
            for table in tables:
                found_tables.append(f"{dataset.dataset_id}.{table.table_id}")
        
        print("\nLooking for expected tables:")
        for expected in expected_tables:
            found = any(expected in table for table in found_tables)
            status = "[OK]" if found else "[MISSING]"
            print(f"{status} {expected}")
            if found:
                matching = [t for t in found_tables if expected in t][0]
                print(f"   Found as: {matching}")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        print("\nTroubleshooting:")
        print("1. Check GCP_PROJECT_ID in .env file")
        print("2. Verify authentication: gcloud auth application-default login")
        print("3. Check BigQuery API is enabled")
        print("4. Verify you have BigQuery permissions")

if __name__ == "__main__":
    print("Checking BigQuery tables...\n")
    check_bigquery_tables()