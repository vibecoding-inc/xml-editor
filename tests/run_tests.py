#!/usr/bin/env python3
"""
Test runner for XML Editor application.

This script discovers and runs all unit and integration tests.
"""

import sys
import unittest
import os


def run_tests(test_type='all', verbosity=2):
    """
    Run tests based on type.
    
    Args:
        test_type: 'unit', 'integration', or 'all'
        verbosity: Test output verbosity level
    
    Returns:
        True if all tests passed, False otherwise
    """
    # Get the directory containing this script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create test loader
    loader = unittest.TestLoader()
    
    # Discover tests based on type
    if test_type == 'unit':
        suite = loader.discover(os.path.join(test_dir, 'unit'), pattern='test_*.py')
        print(f"\n{'=' * 70}")
        print("Running Unit Tests")
        print(f"{'=' * 70}\n")
    elif test_type == 'integration':
        suite = loader.discover(os.path.join(test_dir, 'integration'), pattern='test_*.py')
        print(f"\n{'=' * 70}")
        print("Running Integration Tests")
        print(f"{'=' * 70}\n")
    else:  # 'all'
        suite = unittest.TestSuite()
        suite.addTests(loader.discover(os.path.join(test_dir, 'unit'), pattern='test_*.py'))
        suite.addTests(loader.discover(os.path.join(test_dir, 'integration'), pattern='test_*.py'))
        print(f"\n{'=' * 70}")
        print("Running All Tests (Unit + Integration)")
        print(f"{'=' * 70}\n")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'=' * 70}")
    print("Test Summary")
    print(f"{'=' * 70}")
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"{'=' * 70}\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Parse command line arguments
    test_type = 'all'
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['unit', 'integration', 'all']:
            test_type = arg
        else:
            print(f"Usage: {sys.argv[0]} [unit|integration|all]")
            print(f"  unit         - Run only unit tests")
            print(f"  integration  - Run only integration tests")
            print(f"  all          - Run all tests (default)")
            sys.exit(1)
    
    # Run tests
    success = run_tests(test_type)
    sys.exit(0 if success else 1)
