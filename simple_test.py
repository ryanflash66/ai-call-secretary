"""
Simple test script to verify basic system functionality.
"""
import os
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_environment():
    """Test that the basic environment is working."""
    print("Python version:", sys.version)
    print("Current directory:", os.getcwd())
    print("Files in the current directory:")
    for file in os.listdir('.'):
        print(f"  - {file}")
    
    # Try to load a file to check encoding
    try:
        with open('src/main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        print("\nsrc/main.py content (first 100 chars):", content[:100])
    except Exception as e:
        print(f"\nError reading src/main.py: {e}")
    
    # Try to import a package
    try:
        import yaml
        print("\nSuccessfully imported PyYAML")
    except ImportError:
        print("\nFailed to import PyYAML")
    
    # Try to read the config file
    try:
        with open('config/default.yml', 'r', encoding='utf-8') as f:
            config_content = f.read()
        print("\nconfig/default.yml content (first 100 chars):", config_content[:100])
    except Exception as e:
        print(f"\nError reading config/default.yml: {e}")
    
    return True

if __name__ == "__main__":
    try:
        result = test_environment()
        print("\nTest result:", "PASSED" if result else "FAILED")
    except Exception as e:
        print(f"\nTest failed with exception: {e}")
        sys.exit(1)