# Test Case Input/Output Format Guide

## Overview

Test cases can store input in **JSON format** for structured data, which gets automatically converted to **line-by-line stdin format** when executing code.

---

## Input Format

### JSON Format (Recommended for Database Storage)

```json
{
  "parameter1": value1,
  "parameter2": value2
}
```

### Conversion to stdin

The system automatically converts JSON to line-by-line input:

| JSON Input | stdin Format |
|------------|--------------|
| `{"nums": [2, 7, 11, 15], "target": 9}` | `2 7 11 15`<br>`9` |
| `{"x": 123}` | `123` |
| `{"s": "hello"}` | `hello` |
| `{"arr1": [1, 2, 3], "arr2": [4, 5, 6]}` | `1 2 3`<br>`4 5 6` |

---

## Examples

### Two Sum Problem

**Test Case in Database:**
```json
{
  "input_data": "{\"nums\": [2, 7, 11, 15], \"target\": 9}",
  "expected_output": "[0, 1]"
}
```

**What the Code Receives (stdin):**
```
2 7 11 15
9
```

**Python Template Code:**
```python
def twoSum(nums, target):
    # Write your code here
    hashmap = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in hashmap:
            return [hashmap[complement], i]
        hashmap[num] = i

if __name__ == "__main__":
    nums = [int(e) for e in input().split()]  # Reads: 2 7 11 15
    target = int(input())                      # Reads: 9
    result = twoSum(nums, target)
    print(result)                              # Outputs: [0, 1]
```

**How It Works:**
1. Database stores: `{"nums": [2, 7, 11, 15], "target": 9}`
2. System converts to: `"2 7 11 15\n9"`
3. Code reads line 1: `nums = [2, 7, 11, 15]`
4. Code reads line 2: `target = 9`
5. Code outputs: `[0, 1]`

---

### Reverse Integer Problem

**Test Case in Database:**
```json
{
  "input_data": "{\"x\": 123}",
  "expected_output": "321"
}
```

**What the Code Receives (stdin):**
```
123
```

**Python Template Code:**
```python
def reverse(x):
    # Write your code here
    result = 0
    sign = 1 if x >= 0 else -1
    x = abs(x)
    while x > 0:
        result = result * 10 + x % 10
        x //= 10
    return sign * result

if __name__ == "__main__":
    x = int(input())           # Reads: 123
    result = reverse(x)
    print(result)              # Outputs: 321
```

---

### Longest Substring Problem

**Test Case in Database:**
```json
{
  "input_data": "{\"s\": \"abcabcbb\"}",
  "expected_output": "3"
}
```

**What the Code Receives (stdin):**
```
abcabcbb
```

**Python Template Code:**
```python
def lengthOfLongestSubstring(s):
    # Write your code here
    char_set = set()
    left = 0
    max_length = 0
    
    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_length = max(max_length, right - left + 1)
    
    return max_length

if __name__ == "__main__":
    s = input()                            # Reads: abcabcbb
    result = lengthOfLongestSubstring(s)
    print(result)                          # Outputs: 3
```

---

## Creating Test Cases

### Option 1: JSON Format (Recommended)

```sql
INSERT INTO test_cases (problem_id, input_data, expected_output, is_hidden)
VALUES (
    1,
    '{"nums": [2, 7, 11, 15], "target": 9}',
    '[0, 1]',
    false
);
```

### Option 2: Plain Text Format

```sql
INSERT INTO test_cases (problem_id, input_data, expected_output, is_hidden)
VALUES (
    1,
    '2 7 11 15
9',
    '[0, 1]',
    false
);
```

Both formats work! JSON is clearer for complex inputs.

---

## Output Format

### Expected Output

Can be in any format that matches what `print()` produces:

- **Array/List:** `[0, 1]` or `0 1` or `0, 1`
- **Integer:** `321`
- **String:** `hello`
- **Boolean:** `True` or `true` or `1`

The system **normalizes** outputs before comparison, so these are equivalent:
- `[0, 1]`
- `[0,1]`
- `0, 1`
- `0 1`

---

## Supported Data Types

| Type | JSON Example | stdin Format |
|------|--------------|--------------|
| Integer | `{"x": 123}` | `123` |
| Float | `{"x": 3.14}` | `3.14` |
| String | `{"s": "hello"}` | `hello` |
| Array/List | `{"nums": [1, 2, 3]}` | `1 2 3` |
| Multiple params | `{"a": 5, "b": 10}` | `5`<br>`10` |

---

## Language-Specific Input Parsing

### Python
```python
nums = [int(e) for e in input().split()]  # Array
x = int(input())                           # Integer
s = input()                                # String
```

### JavaScript
```javascript
const nums = lines[0].split(' ').map(Number);  // Array
const x = parseInt(lines[1]);                   // Integer
const s = lines[2];                             // String
```

### C++
```cpp
vector<int> nums;
int temp;
while (cin >> temp) {
    nums.push_back(temp);
    if (cin.peek() == '\n') break;
}
```

### Java
```java
String[] tokens = scanner.nextLine().split(" ");
int[] nums = new int[tokens.length];
for (int i = 0; i < tokens.length; i++) {
    nums[i] = Integer.parseInt(tokens[i]);
}
```

### C
```c
int nums_size;
scanf("%d", &nums_size);
int nums[nums_size];
for (int i = 0; i < nums_size; i++) {
    scanf("%d", &nums[i]);
}
```

---

## Key Points

✅ **JSON input** is automatically converted to stdin format  
✅ **Arrays** become space-separated values  
✅ **Multiple parameters** become separate lines  
✅ **Plain text** input works too (no conversion needed)  
✅ **Output normalization** handles different formats  

This makes test case management easier and more structured! 🎉
