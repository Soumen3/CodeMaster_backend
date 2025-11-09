# Dynamic Code Templates Guide

## Overview
The system now generates **dynamic code templates** based on each problem's specific requirements. Each problem can have its own function signature, parameters, and input/output format.

## How It Works

### 1. Problem Metadata
Each problem in the database stores:
- `function_name`: Name of the solution function (e.g., "twoSum", "lengthOfLongestSubstring")
- `parameters`: JSON array of parameters with name and type
- `return_type`: Expected return type

**Example:**
```json
{
  "function_name": "twoSum",
  "parameters": [
    {"name": "nums", "type": "list[int]"},
    {"name": "target", "type": "int"}
  ],
  "return_type": "list"
}
```

### 2. Template Generation
The `code_template_service.py` generates language-specific templates based on this metadata.

### 3. Frontend Integration
Frontend calls `/problems/{problem_id}/template/{language}` to get the appropriate template.

---

## API Endpoint

### GET `/problems/{problem_id}/template/{language}`

Get dynamic code template for a specific problem and language.

**Parameters:**
- `problem_id`: Problem ID
- `language`: `python` | `javascript` | `cpp` | `java` | `c`

**Response:**
```json
{
  "code": "def twoSum(nums, target):\n    # Write your code here\n    pass\n\nif __name__ == \"__main__\":\n    nums = [int(e) for e in input().split()]\n    target = int(input())\n    result = twoSum(nums, target)\n    print(result)"
}
```

---

## Example Templates

### Problem 1: Two Sum
**Metadata:**
```json
{
  "function_name": "twoSum",
  "parameters": [
    {"name": "nums", "type": "list[int]"},
    {"name": "target", "type": "int"}
  ],
  "return_type": "list"
}
```

**Python Template:**
```python
def twoSum(nums, target):
    # Write your code here
    pass

if __name__ == "__main__":
    nums = [int(e) for e in input().split()]
    target = int(input())
    result = twoSum(nums, target)
    print(result)
```

**JavaScript Template:**
```javascript
function twoSum(nums, target) {
    // Write your code here
    
}

const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const lines = [];
rl.on('line', (line) => {
    lines.push(line);
});

rl.on('close', () => {
    const nums = lines[0].split(' ').map(Number);
    const target = parseInt(lines[1]);
    const result = twoSum(nums, target);
    console.log(result);
});
```

**C++ Template:**
```cpp
#include <iostream>
#include <vector>
#include <string>
using namespace std;

auto twoSum(vector<int>& nums, int target) {
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
    cout << result << endl;
    return 0;
}
```

**Java Template:**
```java
import java.util.*;

public class Solution {
    public static Object twoSum(int[] nums, int target) {
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
        Object result = twoSum(nums, target);
        System.out.println(result);
        scanner.close();
    }
}
```

---

### Problem 2: Longest Substring Without Repeating Characters
**Metadata:**
```json
{
  "function_name": "lengthOfLongestSubstring",
  "parameters": [
    {"name": "s", "type": "str"}
  ],
  "return_type": "int"
}
```

**Python Template:**
```python
def lengthOfLongestSubstring(s):
    # Write your code here
    pass

if __name__ == "__main__":
    s = input()
    result = lengthOfLongestSubstring(s)
    print(result)
```

**JavaScript Template:**
```javascript
function lengthOfLongestSubstring(s) {
    // Write your code here
    
}

const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const lines = [];
rl.on('line', (line) => {
    lines.push(line);
});

rl.on('close', () => {
    const s = lines[0];
    const result = lengthOfLongestSubstring(s);
    console.log(result);
});
```

---

## Supported Parameter Types

| Type | Python | JavaScript | C++ | Java | C |
|------|--------|------------|-----|------|---|
| `int` | `int(input())` | `parseInt(line)` | `int x; cin >> x` | `scanner.nextInt()` | `int x; scanf("%d", &x)` |
| `float` | `float(input())` | `parseFloat(line)` | `double x; cin >> x` | `scanner.nextDouble()` | `double x; scanf("%lf", &x)` |
| `str` | `input()` | `line` | `string x; getline(cin, x)` | `scanner.nextLine()` | `char x[100]; fgets(x, 100, stdin)` |
| `list[int]` | `[int(e) for e in input().split()]` | `line.split(' ').map(Number)` | `vector<int>` | `int[]` | `int arr[]` |

---

## Creating Problems with Templates

### Option 1: Via API (Create Problem)

```bash
curl -X POST http://localhost:8000/problems \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Two Sum",
    "description": "Find two numbers that add up to target",
    "difficulty": "easy",
    "function_name": "twoSum",
    "parameters": "[{\"name\": \"nums\", \"type\": \"list[int]\"}, {\"name\": \"target\", \"type\": \"int\"}]",
    "return_type": "list"
  }'
```

### Option 2: Update Existing Problem

```bash
curl -X PUT http://localhost:8000/problems/1 \
  -H "Content-Type: application/json" \
  -d '{
    "function_name": "twoSum",
    "parameters": "[{\"name\": \"nums\", \"type\": \"list[int]\"}, {\"name\": \"target\", \"type\": \"int\"}]",
    "return_type": "list"
  }'
```

### Option 3: Bulk Update Script

Run the provided script to update all problems:

```bash
cd backend
python scripts/update_problem_templates.py
```

---

## Frontend Integration

### Update CodeEditor Component

```javascript
import { useState, useEffect } from 'react';
import apiClient from '../services/apiClient';

const CodeEditor = ({ problemId }) => {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');

  // Load template when problem or language changes
  useEffect(() => {
    const loadTemplate = async () => {
      try {
        const response = await apiClient.get(
          `/problems/${problemId}/template/${language}`
        );
        setCode(response.data.code);
      } catch (error) {
        console.error('Error loading template:', error);
        // Fallback to default template
        setCode(getDefaultTemplate(language));
      }
    };

    if (problemId) {
      loadTemplate();
    }
  }, [problemId, language]);

  // ... rest of component
};
```

### Service Function

Create `frontend/src/services/templateService.js`:

```javascript
import apiClient from './apiClient';

export const getProblemTemplate = async (problemId, language) => {
  const response = await apiClient.get(
    `/problems/${problemId}/template/${language}`
  );
  return response.data.code;
};
```

---

## Database Schema

### New Columns in `problems` Table

```sql
ALTER TABLE problems 
ADD COLUMN function_name VARCHAR(100) DEFAULT 'solution',
ADD COLUMN parameters TEXT,
ADD COLUMN return_type VARCHAR(50);
```

### Update Existing Data

```sql
-- Example: Update Two Sum problem
UPDATE problems 
SET 
  function_name = 'twoSum',
  parameters = '[{"name": "nums", "type": "list[int]"}, {"name": "target", "type": "int"}]',
  return_type = 'list'
WHERE title = 'Two Sum';

-- Example: Update Longest Substring problem
UPDATE problems 
SET 
  function_name = 'lengthOfLongestSubstring',
  parameters = '[{"name": "s", "type": "str"}]',
  return_type = 'int'
WHERE title = 'Longest Substring Without Repeating Characters';
```

---

## Common Problem Patterns

### Pattern 1: Array + Target
```json
{
  "function_name": "twoSum",
  "parameters": [
    {"name": "nums", "type": "list[int]"},
    {"name": "target", "type": "int"}
  ],
  "return_type": "list"
}
```

### Pattern 2: String Processing
```json
{
  "function_name": "isPalindrome",
  "parameters": [
    {"name": "s", "type": "str"}
  ],
  "return_type": "bool"
}
```

### Pattern 3: Multiple Arrays
```json
{
  "function_name": "mergeTwoLists",
  "parameters": [
    {"name": "list1", "type": "list[int]"},
    {"name": "list2", "type": "list[int]"}
  ],
  "return_type": "list"
}
```

### Pattern 4: Single Number
```json
{
  "function_name": "reverse",
  "parameters": [
    {"name": "x", "type": "int"}
  ],
  "return_type": "int"
}
```

---

## Benefits

1. ✅ **Problem-Specific**: Each problem has its own signature
2. ✅ **Clean Code**: Users write only the solution logic
3. ✅ **Multi-Language**: Consistent across all languages
4. ✅ **No Boilerplate**: Input/output handled automatically
5. ✅ **Flexible**: Easy to add new problem types
6. ✅ **Maintainable**: Centralized template generation

---

## Testing Templates

### Test Template Generation

```python
from app.services.code_template_service import get_code_template

# Two Sum template
params = [
    {"name": "nums", "type": "list[int]"},
    {"name": "target", "type": "int"}
]

python_code = get_code_template("python", "twoSum", params, "list")
print(python_code)
```

### Test via API

```bash
curl http://localhost:8000/problems/1/template/python
```

---

## Migration Checklist

- [x] Add columns to Problem model
- [x] Update ProblemBase, ProblemCreate, ProblemUpdate schemas
- [x] Create code_template_service.py
- [x] Add /template endpoint to problems router
- [x] Create update script for existing problems
- [ ] Run migration to add columns to database
- [ ] Update existing problems with template data
- [ ] Update frontend CodeEditor to fetch dynamic templates
- [ ] Test all languages with sample problems
- [ ] Update problem creation UI to include template fields

---

## Next Steps

1. **Restart Backend** - The new columns will be created automatically
2. **Run Update Script** - Populate template data for existing problems
3. **Update Frontend** - Fetch templates from API instead of using hardcoded ones
4. **Test** - Verify templates work for all languages

```bash
# Restart backend
cd backend
# Server will auto-create new columns

# Update existing problems
python scripts/update_problem_templates.py

# Frontend will automatically use new templates!
```
