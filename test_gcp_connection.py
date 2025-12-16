"""
Test GCP Connection
Simple script to verify GCP authentication and project access
"""

import os
from google.cloud import bigquery

def test_gcp_connection():
    """Test connection to GCP project"""
    
    print("=" * 60)
    print("Testing GCP Connection")
    print("=" * 60)
    
    # Get project ID from environment or use default
    project_id = os.environ.get('GCP_PROJECT_ID', 'ccibt-hack25ww7-730')
    
    print(f"\n[OK] Project ID: {project_id}")
    
    try:
        # Initialize BigQuery client
        client = bigquery.Client(project=project_id)
        
        print(f"[OK] BigQuery client initialized successfully")
        
        # List datasets (if any exist)
        datasets = list(client.list_datasets())
        
        if datasets:
            print(f"\n[OK] Found {len(datasets)} dataset(s):")
            for dataset in datasets:
                print(f"  - {dataset.dataset_id}")
        else:
            print("\n[OK] No datasets found (this is normal for a new project)")
        
        print("\n" + "=" * 60)
        print("SUCCESS: GCP Connection Test Passed")
        print("=" * 60)
        print("\nYour environment is ready to use GCP services!")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error connecting to GCP: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're authenticated: gcloud auth application-default login")
        print("2. Check your project ID is correct")
        print("3. Ensure BigQuery API is enabled")
        return False

if __name__ == "__main__":
    test_gcp_connection()