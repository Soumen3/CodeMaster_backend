"""
Test script to demonstrate dynamic code template generation.
"""
from app.services.code_template_service import get_code_template

print("=" * 80)
print("DYNAMIC CODE TEMPLATE DEMONSTRATION")
print("=" * 80)

# Example 1: Two Sum
print("\n📝 PROBLEM 1: Two Sum")
print("-" * 80)
params_two_sum = {
    "nums": "list[int]",
    "target": "int"
}

print("\n🐍 PYTHON:")
print(get_code_template("python", "twoSum", params_two_sum, "list"))

print("\n" + "=" * 80)

# Example 2: Longest Substring
print("\n📝 PROBLEM 2: Longest Substring Without Repeating Characters")
print("-" * 80)
params_substring = {
    "s": "str"
}

print("\n🐍 PYTHON:")
print(get_code_template("python", "lengthOfLongestSubstring", params_substring, "int"))

print("\n💛 JAVASCRIPT:")
print(get_code_template("javascript", "lengthOfLongestSubstring", params_substring, "int"))

print("\n" + "=" * 80)

# Example 3: Reverse Integer
print("\n📝 PROBLEM 3: Reverse Integer")
print("-" * 80)
params_reverse = {
    "x": "int"
}

print("\n🐍 PYTHON:")
print(get_code_template("python", "reverse", params_reverse, "int"))

print("\n⚡ C++:")
print(get_code_template("cpp", "reverse", params_reverse, "int"))

print("\n" + "=" * 80)
print("✅ Dynamic template generation working!")
print("=" * 80)
