#!/usr/bin/env python3
"""
Comprehensive test runner for the QCanvas project.
Runs all unit tests, integration tests, and end-to-end tests.
"""

import unittest
import sys
import os
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def discover_and_run_tests():
    """Discover and run all tests in the project."""
    print("🧪 QCanvas Comprehensive Test Suite")
    print("=" * 50)
    
    # Test discovery patterns
    test_patterns = [
        'tests/unit/test_*.py',
        'tests/unit/test_qasm3/test_*.py',
        'tests/integration/test_*.py',
        'tests/e2e/test_*.py',
    ]
    
    # Discover all test modules
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    total_tests = 0
    test_modules = []
    
    for pattern in test_patterns:
        pattern_path = project_root / pattern
        if pattern_path.parent.exists():
            # Find all test files matching the pattern
            for test_file in pattern_path.parent.glob(pattern_path.name):
                if test_file.is_file() and test_file.name.startswith('test_'):
                    module_name = f"{test_file.parent.name}.{test_file.stem}"
                    if 'test_qasm3' in str(test_file):
                        module_name = f"unit.test_qasm3.{test_file.stem}"
                    
                    try:
                        # Import and load tests
                        module = __import__(module_name, fromlist=[''])
                        module_suite = loader.loadTestsFromModule(module)
                        suite.addTest(module_suite)
                        
                        test_count = module_suite.countTestCases()
                        total_tests += test_count
                        test_modules.append((test_file.name, test_count))
                        
                        print(f"✅ Loaded {test_file.name}: {test_count} tests")
                    except Exception as e:
                        print(f"❌ Failed to load {test_file.name}: {e}")
    
    print(f"\n📊 Total tests discovered: {total_tests}")
    print(f"📁 Test modules: {len(test_modules)}")
    print("\n" + "=" * 50)
    
    # Run tests
    print("🚀 Running tests...")
    start_time = time.time()
    
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    print("\n" + "=" * 50)
    print("📈 Test Results Summary")
    print("=" * 50)
    print(f"Total tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"Duration: {duration:.2f} seconds")
    
    if result.failures:
        print(f"\n❌ Failures ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n💥 Errors ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Return success status
    return len(result.failures) == 0 and len(result.errors) == 0


def run_specific_test_category(category):
    """Run tests for a specific category."""
    categories = {
        'unit': 'tests/unit/test_*.py',
        'qasm3': 'tests/unit/test_qasm3/test_*.py',
        'integration': 'tests/integration/test_*.py',
        'e2e': 'tests/e2e/test_*.py',
    }
    
    if category not in categories:
        print(f"❌ Unknown category: {category}")
        print(f"Available categories: {', '.join(categories.keys())}")
        return False
    
    print(f"🎯 Running {category} tests...")
    
    # Create a custom test suite for the category
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    pattern_path = project_root / categories[category]
    if pattern_path.parent.exists():
        for test_file in pattern_path.parent.glob(pattern_path.name):
            if test_file.is_file() and test_file.name.startswith('test_'):
                module_name = f"{test_file.parent.name}.{test_file.stem}"
                if 'test_qasm3' in str(test_file):
                    module_name = f"unit.test_qasm3.{test_file.stem}"
                
                try:
                    module = __import__(module_name, fromlist=[''])
                    module_suite = loader.loadTestsFromModule(module)
                    suite.addTest(module_suite)
                except Exception as e:
                    print(f"❌ Failed to load {test_file.name}: {e}")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0


def main():
    """Main test runner function."""
    if len(sys.argv) > 1:
        category = sys.argv[1].lower()
        success = run_specific_test_category(category)
    else:
        success = discover_and_run_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
