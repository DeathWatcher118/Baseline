#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify GCP Cloud Run services are responding
"""

import requests
import json
import sys
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Service URLs
BASELINE_SERVICE_URL = "https://baseline2-git-jgscwa2bzq-uc.a.run.app"
ANALYSIS_SERVICE_URL = "https://analysisagent-git-jgscwa2bzq-uc.a.run.app"

def test_service(service_name, url):
    """Test a service endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing {service_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        # Test basic connectivity
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sending GET request...")
        response = requests.get(url, timeout=30)
        
        print(f"[OK] Status Code: {response.status_code}")
        print(f"[OK] Response Time: {response.elapsed.total_seconds():.2f}s")
        print(f"[OK] Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"[OK] Content-Length: {len(response.content)} bytes")
        
        # Show response preview
        print(f"\nResponse Preview (first 500 chars):")
        print("-" * 60)
        content = response.text[:500]
        print(content)
        if len(response.text) > 500:
            print("... (truncated)")
        print("-" * 60)
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"[ERROR] Request timed out after 30 seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection failed - {str(e)}")
        return False
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")
        return False

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("GCP Cloud Run Services Connection Test")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {}
    
    # Test Baseline Service
    results['baseline'] = test_service("Baseline Calculator Service", BASELINE_SERVICE_URL)
    
    # Test Analysis Service
    results['analysis'] = test_service("Anomaly Analysis Agent Service", ANALYSIS_SERVICE_URL)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Baseline Service: {'[PASS]' if results['baseline'] else '[FAIL]'}")
    print(f"Analysis Service: {'[PASS]' if results['analysis'] else '[FAIL]'}")
    print(f"\nOverall: {'[ALL SERVICES RESPONDING]' if all(results.values()) else '[SOME SERVICES FAILED]'}")
    print(f"{'='*60}\n")
    
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit(main())