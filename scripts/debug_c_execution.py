"""
Debug C code execution with input conversion
"""
import sys
import os
import subprocess
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.compile_problem_service import convert_input_format

# Test input conversion
input_json = '{"nums": [2,7,11,15], "target": 9}'
print("Original JSON input:")
print(input_json)
print()

converted = convert_input_format(input_json)
print("Converted stdin format:")
print(repr(converted))
print()

print("Actual stdin (what the C program receives):")
print(converted)
print()

# Now let's test with the actual C code
c_code = """#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int* twoSum(int nums[], int nums_size, int target) {
    static int result[2];

    for (int i = 0; i < nums_size; i++) {
        for (int j = i + 1; j < nums_size; j++) {
            if (nums[i] + nums[j] == target) {
                result[0] = i;
                result[1] = j;
                return result;
            }
        }
    }

    result[0] = -1;
    result[1] = -1;
    return result;
}

int main() {
    // Read array nums
    char line[10000];
    fgets(line, sizeof(line), stdin);
    int nums[1000];
    int nums_size = 0;
    char *token = strtok(line, " \\n");
    while (token != NULL) {
        nums[nums_size++] = atoi(token);
        token = strtok(NULL, " \\n");
    }
    int target;
    scanf("%d", &target);
    
    printf("DEBUG: nums_size = %d\\n", nums_size);
    printf("DEBUG: nums = [");
    for (int i = 0; i < nums_size; i++) {
        printf("%d", nums[i]);
        if (i < nums_size - 1) printf(", ");
    }
    printf("]\\n");
    printf("DEBUG: target = %d\\n", target);
    
    int* result = twoSum(nums, nums_size, target);
    printf("[");
    for (int i = 0; i < 2; i++) {
        printf("%d", result[i]);
        if (i < 1) printf(", ");
    }
    printf("]\\n");
    
    return 0;
}
"""

# Write C code to temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
    f.write(c_code)
    source_file = f.name

try:
    # Compile
    executable = source_file.replace('.c', '.exe')
    compile_result = subprocess.run(
        ['gcc', source_file, '-o', executable],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if compile_result.returncode != 0:
        print(f"Compilation error: {compile_result.stderr}")
    else:
        print("Compilation successful!")
        print()
        
        # Run with converted input
        print("Running C program with converted input...")
        print("=" * 60)
        result = subprocess.run(
            [executable],
            input=converted,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print("=" * 60)
finally:
    # Cleanup
    if os.path.exists(source_file):
        os.unlink(source_file)
    if 'executable' in locals() and os.path.exists(executable):
        os.unlink(executable)
