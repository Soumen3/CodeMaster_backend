"""
Test Java template generation
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.code_template_service import generate_java_template

# Test Two Sum
print("=" * 60)
print("Two Sum - Java Template")
print("=" * 60)
params = {
    "nums": "list[int]",
    "target": "int"
}
template = generate_java_template("twoSum", params, "list[int]")
print(template)
print()

# Test with single integer
print("=" * 60)
print("Reverse Integer - Java Template")
print("=" * 60)
params = {
    "x": "int"
}
template = generate_java_template("reverse", params, "int")
print(template)
