"""
Minimal test that doesn't depend on conftest.py.
"""
import os
import sys
import pytest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Create an empty test
def test_minimal():
    """A minimal test that should always pass."""
    assert True

# Check Python version
def test_python_version():
    """Test that Python version is compatible."""
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 8