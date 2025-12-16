#!/usr/bin/env python3
"""
Test access to the BigQuery dataset
"""

from google.cloud import bigquery

def test_access():
    """Test different ways to access the dataset"""
    
    client = bigquery.Client(project='ccibt-hack25ww7-730')
    
    print("Testing BigQuery Data Access")
    print("=" * 60)
    
    # Try different dataset reference formats
    dataset_formats = [
        'datasets-ccibt-hack25ww7-730.uc3-volume-spikes-analyzer',
        'ccibt-hack25ww7-730.uc3-volume-spikes-analyzer',
        'uc3-volume-spikes-analyzer',
    ]
    
    for dataset_id in dataset_formats:
        print(f"\nTrying: {dataset_id}")
        try:
            tables = list(client.list_tables(dataset_id))
            print(f"✓ SUCCESS! Found {len(tables)} tables")
            for table in tables:
                print(f"  - {table.table_id}")
            break
        except Exception as e:
            print(f"X Failed: {str(e)[:100]}")
    
    # Try listing all datasets in current project
    print("\n" + "=" * 60)
    print("Datasets in current project (ccibt-hack25ww7-730):")
    try:
        datasets = list(client.list_datasets())
        if datasets:
            for dataset in datasets:
                print(f"  - {dataset.dataset_id}")
        else:
            print("  No datasets found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_access()