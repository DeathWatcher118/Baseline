"""
Check if all required packages are installed
"""
import sys

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"[OK] {package_name}: version {version}")
        return True
    except ImportError as e:
        print(f"[MISSING] {package_name}")
        return False

def main():
    print("=" * 80)
    print("CHECKING REQUIRED PACKAGES")
    print("=" * 80)
    print()
    
    packages = [
        ('google-cloud-bigquery', 'google.cloud.bigquery'),
        ('google-cloud-aiplatform', 'google.cloud.aiplatform'),
        ('google-cloud-storage', 'google.cloud.storage'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('pyyaml', 'yaml'),
        ('python-dotenv', 'dotenv'),
    ]
    
    results = []
    for package_name, import_name in packages:
        results.append(check_package(package_name, import_name))
    
    print()
    print("=" * 80)
    print(f"RESULTS: {sum(results)}/{len(results)} packages installed")
    print("=" * 80)
    
    if not all(results):
        print()
        print("To install missing packages, run:")
        print("  pip install -r requirements.txt")
        print()
        sys.exit(1)
    else:
        print()
        print("All required packages are installed!")
        print()
        sys.exit(0)

if __name__ == "__main__":
    exit(main())