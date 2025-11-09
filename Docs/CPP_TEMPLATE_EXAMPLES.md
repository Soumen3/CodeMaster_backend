# C++ Template Examples

## Two Sum Problem

**Function Signature:**
```cpp
vector<int> twoSum(vector<int>& nums, int target)
```

**Generated Template:**
```cpp
#include <iostream>
#include <vector>
#include <string>
using namespace std;

vector<int> twoSum(vector<int>& nums, int target) {
    // Write your code here
    
}

int main() {
    vector<int> nums;
    int temp;
    while (cin >> temp) {
        nums.push_back(temp);
        if (cin.peek() == '\n') break;
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
```

**Input Format:**
```
2 7 11 15
9
```

**User Only Needs to Implement:**
```cpp
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
```

**Output:**
```
[0, 1]
```

---

## Reverse Integer Problem

**Generated Template:**
```cpp
#include <iostream>
#include <vector>
#include <string>
using namespace std;

int reverse(int x) {
    // Write your code here
    
}

int main() {
    int x;
    cin >> x;
    auto result = reverse(x);
    cout << result << endl;
    return 0;
}
```

**Input Format:**
```
123
```

**User Implementation:**
```cpp
int reverse(int x) {
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

✅ **Input parsing included** - Reads arrays and integers automatically  
✅ **Function called automatically** - main() calls your function  
✅ **Output formatted correctly** - Prints vectors as `[1, 2]` format  
✅ **No compilation errors** - Proper vector printing (no `cout << vector` errors)  

## Important Notes

- **Vector returns**: Automatically formatted as `[element1, element2, ...]`
- **Scalar returns**: Printed directly with `cout << result`
- **Input**: Arrays are space-separated on one line
- **Parsing**: Automatically stops reading array at newline

## Common Return Types

| Return Type | Output Format | Example |
|-------------|---------------|---------|
| `int` | Plain number | `123` |
| `double` | Plain number | `3.14` |
| `string` | Plain string | `hello` |
| `vector<int>` | JSON array | `[0, 1]` |

---

## Fixed Issue

**Before (Error):**
```cpp
cout << result << endl;  // ❌ Error: no match for operator<<
```

**After (Fixed):**
```cpp
cout << "[";
for (int i = 0; i < result.size(); i++) {
    cout << result[i];
    if (i < result.size() - 1) cout << ", ";
}
cout << "]" << endl;  // ✅ Works!
```

The template now properly prints vectors in JSON array format! 🎉
