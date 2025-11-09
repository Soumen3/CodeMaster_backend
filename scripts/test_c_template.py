"""
Test C template generation
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.code_template_service import generate_c_template

# Test Two Sum
print("=" * 60)
print("Two Sum - C Template")
print("=" * 60)
params = {
    "nums": "list[int]",
    "target": "int"
}
template = generate_c_template("twoSum", params, "list[int]")
print(template)
print()

# Test with single integer
print("=" * 60)
print("Reverse Integer - C Template")
print("=" * 60)
params = {
    "x": "int"
}
template = generate_c_template("reverse", params, "int")
print(template)
print()

# Test with string
print("=" * 60)
print("Is Palindrome - C Template")
print("=" * 60)
params = {
    "s": "string"
}
template = generate_c_template("isPalindrome", params, "bool")
print(template)
