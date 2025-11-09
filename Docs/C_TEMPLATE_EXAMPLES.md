# C Template Examples

## Two Sum Problem

**Function Signature:**
```c
int* twoSum(int nums[], int nums_size, int target)
```

**Generated Template:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int* twoSum(int nums[], int nums_size, int target) {
    // Write your code here
    
}

int main() {
    // Read array nums
    char line[10000];
    fgets(line, sizeof(line), stdin);
    int nums[1000];
    int nums_size = 0;
    char *token = strtok(line, " \n");
    while (token != NULL) {
        nums[nums_size++] = atoi(token);
        token = strtok(NULL, " \n");
    }
    int target;
    scanf("%d", &target);
    
    int* result = twoSum(nums, nums_size, target);
    // Print array result (assuming size 2 for Two Sum)
    // Modify the loop size based on your problem's return array size
    printf("[");
    for (int i = 0; i < 2; i++) {
        printf("%d", result[i]);
        if (i < 1) printf(", ");
    }
    printf("]\n");
    
    return 0;
}
```

**Input Format:**
```
2 7 11 15
9
```

**Note:** The array is sent as space-separated values on one line. The C template automatically counts the elements using `strtok()`.

**User Only Needs to Implement:**
```c
int* twoSum(int nums[], int nums_size, int target) {
    // Create result array
    int* result = (int*)malloc(2 * sizeof(int));
    
    // Your logic here
    for (int i = 0; i < nums_size; i++) {
        for (int j = i + 1; j < nums_size; j++) {
            if (nums[i] + nums[j] == target) {
                result[0] = i;
                result[1] = j;
                return result;
            }
        }
    }
    
    return result;
}
```

---

## Reverse Integer Problem

**Generated Template:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int reverse(int x) {
    // Write your code here
    
}

int main() {
    int x;
    scanf("%d", &x);
    
    int result = reverse(x);
    printf("%d\n", result);
    
    return 0;
}
```

**Input Format:**
```
123
```

**User Only Needs to Implement:**
```c
int reverse(int x) {
    int reversed = 0;
    while (x != 0) {
        reversed = reversed * 10 + x % 10;
        x /= 10;
    }
    return reversed;
}
```

---

## Features

✅ **Input parsing code is included by default** - Users don't have to write scanf/printf boilerplate  
✅ **Function is called automatically** - main() already calls the user's function  
✅ **Output is printed** - Result is printed with appropriate format  
✅ **Dynamic based on problem** - Each problem gets its own function signature and input parsing  

## Supported Parameter Types

- `int` - Integer input
- `float`/`double` - Floating-point input
- `string`/`str` - String input (max 1000 chars)
- `list[int]` - Integer array with size parameter
- `bool` - Boolean (returned as int: 0/1)
