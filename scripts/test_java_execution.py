"""
Test Java execution with the actual service
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.compile_problem_service import execute_java, convert_input_format

# Test code
java_code = """import java.util.*;

public class Solution {
    public static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                return new int[]{map.get(complement), i};
            }
            map.put(nums[i], i);
        }
        
        return new int[]{-1, -1};
    }
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String[] tokens = scanner.nextLine().split(" ");
        int[] nums = new int[tokens.length];
        for (int i = 0; i < tokens.length; i++) {
            nums[i] = Integer.parseInt(tokens[i]);
        }
        int target = scanner.nextInt();
        int[] result = twoSum(nums, target);
        System.out.print("[");
        for (int i = 0; i < result.length; i++) {
            System.out.print(result[i]);
            if (i < result.length - 1) System.out.print(", ");
        }
        System.out.println("]");
        scanner.close();
    }
}
"""

# Convert input
input_json = '{"nums": [2,7,11,15], "target": 9}'
converted_input = convert_input_format(input_json)

print("Testing Java execution...")
print("=" * 60)
print(f"Input: {input_json}")
print(f"Converted: {repr(converted_input)}")
print()

output, error = execute_java(java_code, converted_input)

if error:
    print(f"❌ Error: {error}")
else:
    print(f"✅ Success!")
    print(f"Output: {output.strip()}")
    print(f"Expected: [0, 1]")

print("=" * 60)
