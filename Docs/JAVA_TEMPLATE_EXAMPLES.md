# Java Template Examples

## Two Sum Problem

**Function Signature:**
```java
public static int[] twoSum(int[] nums, int target)
```

**Generated Template:**
```java
import java.util.*;

public class Solution {
    public static int[] twoSum(int[] nums, int target) {
        // Write your code here
        return null;
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
```

**Input Format:**
```
2 7 11 15
9
```

**User Only Needs to Implement:**
```java
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
```

**Output:**
```
[0, 1]
```

---

## Reverse Integer Problem

**Generated Template:**
```java
import java.util.*;

public class Solution {
    public static int reverse(int x) {
        // Write your code here
        return null;
    }
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int x = scanner.nextInt();
        int result = reverse(x);
        System.out.println(result);
        scanner.close();
    }
}
```

**Input Format:**
```
123
```

**User Implementation:**
```java
public static int reverse(int x) {
    int result = 0;
    while (x != 0) {
        result = result * 10 + x % 10;
        x /= 10;
    }
    return result;
}
```

**Output:**
```
321
```

---

## Key Features

✅ **Input parsing included** - Scanner reads arrays and integers automatically  
✅ **Function called automatically** - main() calls your function  
✅ **Output formatted correctly** - Prints arrays as `[1, 2]` format  
✅ **No memory address printing** - Proper array printing (no `[I@10f87f48` errors)  

## Important Notes

- **Array returns**: Automatically formatted as `[element1, element2, ...]`
- **Scalar returns**: Printed directly with `System.out.println()`
- **Input**: Arrays are space-separated on one line
- **Parsing**: Uses `split(" ")` to parse array elements

## Common Return Types

| Return Type | Output Format | Example |
|-------------|---------------|---------|
| `int` | Plain number | `123` |
| `double` | Plain number | `3.14` |
| `String` | Plain string | `hello` |
| `int[]` | JSON array | `[0, 1]` |

---

## Fixed Issue

**Before (Error):**
```java
System.out.println(result);  // ❌ Prints: [I@10f87f48 (memory address)
```

**After (Fixed):**
```java
System.out.print("[");
for (int i = 0; i < result.length; i++) {
    System.out.print(result[i]);
    if (i < result.length - 1) System.out.print(", ");
}
System.out.println("]");  // ✅ Prints: [0, 1]
```

The template now properly prints arrays in JSON array format instead of memory addresses! 🎉
