"""
Test C++ execution with the actual service
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.compile_problem_service import execute_cpp, convert_input_format

# Test code
cpp_code = """#include <iostream>
#include <vector>
#include <string>
using namespace std;

vector<int> twoSum(vector<int>& nums, int target) {
    vector<int> result;
    for (int i = 0; i < nums.size(); i++) {
        for (int j = i + 1; j < nums.size(); j++) {
            if (nums[i] + nums[j] == target) {
                result.push_back(i);
                result.push_back(j);
                return result;
            }
        }
    }
    return {-1, -1};
}

int main() {
    vector<int> nums;
    int temp;
    while (cin >> temp) {
        nums.push_back(temp);
        if (cin.peek() == '\\n') break;
    }
    int target;
    cin >> target;
    auto result = twoSum(nums, target);
    cout << "[";
    for (int i = 0; i < result.size(); i++) {
        cout << result[i];
        if (i < result.size() - 1) cout << ", ";
    }
    cout << "]" << endl;
    return 0;
}
"""

# Convert input
input_json = '{"nums": [2,7,11,15], "target": 9}'
converted_input = convert_input_format(input_json)

print("Testing C++ execution...")
print("=" * 60)
print(f"Input: {input_json}")
print(f"Converted: {repr(converted_input)}")
print()

output, error = execute_cpp(cpp_code, converted_input)

if error:
    print(f"❌ Error: {error}")
else:
    print(f"✅ Success!")
    print(f"Output: {output.strip()}")
    print(f"Expected: [0, 1]")

print("=" * 60)
