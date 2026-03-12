#!/usr/bin/env python
"""
Quick test runner for dashboard integrity property tests
"""
import sys
import pytest

if __name__ == "__main__":
    # Run the dashboard integrity property tests
    exit_code = pytest.main([
        "tests/test_property_dashboard_integrity.py",
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
    
    if exit_code == 0:
        print("\n✓ All dashboard integrity property tests passed!")
    else:
        print(f"\n✗ Tests failed with exit code: {exit_code}")
    
    sys.exit(exit_code)
