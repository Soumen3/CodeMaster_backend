"""
Test UTF-8 encoding support in Python execution
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.compile_problem_service import execute_python, convert_input_format

# Test code with Unicode characters
code_with_unicode = """def twoSum(nums, target):
    # Write your code here
    num_map = {}  # store value → index mapping
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    return [-1, -1]  # if no solution found

if __name__ == "__main__":
    nums = [int(e) for e in input().split()]
    target = int(input())
    result = twoSum(nums, target)
    print(result)
"""

# Convert input
input_json = '{"nums": [2,7,11,15], "target": 9}'
converted_input = convert_input_format(input_json)

print("Testing Python execution with Unicode characters...")
print("=" * 60)
print(f"Input: {input_json}")
print(f"Converted: {repr(converted_input)}")
print()

output, error = execute_python(code_with_unicode, converted_input)

if error:
    print(f"❌ Error: {error}")
else:
    print(f"✅ Success!")
    print(f"Output: {output}")

print("=" * 60)
