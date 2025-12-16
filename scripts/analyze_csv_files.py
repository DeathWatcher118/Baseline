#!/usr/bin/env python3
"""
Analyze the downloaded CSV files
"""

import pandas as pd
import json
from pathlib import Path

def analyze_csv_file(filepath):
    """Analyze a single CSV file"""
    
    print(f"\n{'='*80}")
    print(f"Analyzing: {filepath.name}")
    print(f"{'='*80}")
    
    try:
        # Read CSV
        df = pd.read_csv(filepath)
        
        # Basic info
        print(f"\nBasic Information:")
        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  File Size: {filepath.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Column info
        print(f"\nColumns ({len(df.columns)}):")
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            unique_count = df[col].nunique()
            print(f"  - {col}")
            print(f"      Type: {dtype}")
            print(f"      Nulls: {null_count} ({null_pct:.1f}%)")
            print(f"      Unique: {unique_count:,}")
            
            # Sample values
            if unique_count <= 10:
                print(f"      Values: {df[col].unique().tolist()}")
            else:
                print(f"      Sample: {df[col].head(3).tolist()}")
        
        # Sample data
        print(f"\nSample Data (first 5 rows):")
        print(df.head().to_string(index=False))
        
        # Statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            print(f"\nNumeric Column Statistics:")
            print(df[numeric_cols].describe().to_string())
        
        # Date columns
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_cols:
            print(f"\nDate/Time Columns:")
            for col in date_cols:
                try:
                    df[col] = pd.to_datetime(df[col])
                    print(f"  {col}:")
                    print(f"    Min: {df[col].min()}")
                    print(f"    Max: {df[col].max()}")
                    print(f"    Range: {(df[col].max() - df[col].min()).days} days")
                except:
                    print(f"  {col}: Could not parse as datetime")
        
        # Return summary
        return {
            'filename': filepath.name,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'size_mb': filepath.stat().st_size / 1024 / 1024
        }
        
    except Exception as e:
        print(f"Error analyzing {filepath.name}: {e}")
        return None

def main():
    """Analyze all CSV files in data directory"""
    
    data_dir = Path('data')
    csv_files = list(data_dir.glob('*.csv'))
    
    if not csv_files:
        print("No CSV files found in data/ directory")
        return
    
    print(f"Found {len(csv_files)} CSV file(s)")
    
    summaries = []
    for csv_file in csv_files:
        summary = analyze_csv_file(csv_file)
        if summary:
            summaries.append(summary)
    
    # Save summary
    summary_data = {
        'analyzed_at': pd.Timestamp.now().isoformat(),
        'file_count': len(summaries),
        'files': summaries
    }
    
    with open('data_analysis_summary.json', 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Analysis complete! Summary saved to: data_analysis_summary.json")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()