"""
Test input format conversion
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.compile_problem_service import convert_input_format

# Test cases
test_cases = [
    {
        "name": "Two Sum - JSON object",
        "input": '{"nums": [2, 7, 11, 15], "target": 9}',
        "expected": "2 7 11 15\n9"
    },
    {
        "name": "Single integer",
        "input": '{"x": 123}',
        "expected": "123"
    },
    {
        "name": "String input",
        "input": '{"s": "hello"}',
        "expected": "hello"
    },
    {
        "name": "Multiple parameters",
        "input": '{"arr1": [1, 2, 3], "arr2": [4, 5, 6]}',
        "expected": "1 2 3\n4 5 6"
    },
    {
        "name": "Plain text (not JSON)",
        "input": "123\n456",
        "expected": "123\n456"
    },
    {
        "name": "Array only",
        "input": '[2, 7, 11, 15]',
        "expected": "2 7 11 15"
    }
]

print("=" * 60)
print("Testing Input Format Conversion")
print("=" * 60)

for test in test_cases:
    print(f"\nTest: {test['name']}")
    print(f"Input: {test['input']}")
    result = convert_input_format(test['input'])
    print(f"Result: {repr(result)}")
    print(f"Expected: {repr(test['expected'])}")
    
    if result == test['expected']:
        print("✅ PASSED")
    else:
        print("❌ FAILED")

print("\n" + "=" * 60)
