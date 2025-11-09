# Dynamic Code Templates - New Format

## Parameter Format

Parameters are now stored as a simple JSON object:

```json
{
  "parameter_name": "type",
  "parameter2_name": "type"
}
```

## Examples

### Two Sum Problem

**Database Entry:**
```json
{
  "function_name": "twoSum",
  "parameters": "{\"nums\": \"list[int]\", \"target\": \"int\"}",
  "return_type": "list"
}
```

**Generated Python Template:**
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

---

### Longest Substring Problem

**Database Entry:**
```json
{
  "function_name": "lengthOfLongestSubstring",
  "parameters": "{\"s\": \"str\"}",
  "return_type": "int"
}
```

**Generated Python Template:**
```python
def lengthOfLongestSubstring(s):
    # Write your code here
    pass

if __name__ == "__main__":
    s = input()
    result = lengthOfLongestSubstring(s)
    print(result)
```

---

## Creating a Problem with Template

### Via SQL

```sql
INSERT INTO problems (title, description, difficulty, function_name, parameters, return_type)
VALUES (
    'Two Sum',
    'Find two numbers that add up to target',
    'easy',
    'twoSum',
    '{"nums": "list[int]", "target": "int"}',
    'list'
);
```

### Via API

```bash
curl -X POST http://localhost:8000/problems \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Two Sum",
    "description": "Find two numbers that add up to target",
    "difficulty": "easy",
    "function_name": "twoSum",
    "parameters": "{\"nums\": \"list[int]\", \"target\": \"int\"}",
    "return_type": "list"
  }'
```

### Via Python Script

```python
from app.database.connection import SessionLocal
from app.database.models import Problem
import json

db = SessionLocal()

problem = Problem(
    title="Two Sum",
    description="Find two numbers that add up to target",
    difficulty="easy",
    function_name="twoSum",
    parameters=json.dumps({"nums": "list[int]", "target": "int"}),
    return_type="list"
)

db.add(problem)
db.commit()
db.close()
```

---

## API Usage

### Get Template

```bash
GET /problems/{problem_id}/template/{language}
```

**Example:**
```bash
curl http://localhost:8000/problems/1/template/python
```

**Response:**
```json
{
  "code": "def twoSum(nums, target):\n    # Write your code here\n    pass\n\nif __name__ == \"__main__\":\n    nums = [int(e) for e in input().split()]\n    target = int(input())\n    result = twoSum(nums, target)\n    print(result)"
}
```

---

## Supported Types

- `int` - Integer
- `float` - Float/Double
- `str` / `string` - String
- `list[int]` / `list<int>` / `array` - Integer array/list
- `bool` - Boolean

---

## Complete Examples

### Example 1: Single String Parameter
```json
{
  "function_name": "isPalindrome",
  "parameters": "{\"s\": \"str\"}",
  "return_type": "bool"
}
```

### Example 2: Multiple Integer Parameters
```json
{
  "function_name": "add",
  "parameters": "{\"a\": \"int\", \"b\": \"int\"}",
  "return_type": "int"
}
```

### Example 3: Array and Target
```json
{
  "function_name": "search",
  "parameters": "{\"nums\": \"list[int]\", \"target\": \"int\"}",
  "return_type": "int"
}
```

### Example 4: Multiple Arrays
```json
{
  "function_name": "merge",
  "parameters": "{\"arr1\": \"list[int]\", \"arr2\": \"list[int]\"}",
  "return_type": "list[int]"
}
```

---

## Benefits of New Format

✅ **Simpler**: Cleaner JSON structure  
✅ **Readable**: Easy to understand at a glance  
✅ **Maintains Order**: Dictionary preserves insertion order in Python 3.7+  
✅ **Less Verbose**: Shorter JSON strings  
✅ **Easy Parsing**: Direct key-value access  

---

## Migration Guide

### Old Format
```json
"parameters": "[{\"name\": \"nums\", \"type\": \"list[int]\"}, {\"name\": \"target\", \"type\": \"int\"}]"
```

### New Format
```json
"parameters": "{\"nums\": \"list[int]\", \"target\": \"int\"}"
```

### Conversion Script
```python
import json

# Old format
old_params = '[{"name": "nums", "type": "list[int]"}, {"name": "target", "type": "int"}]'
old_list = json.loads(old_params)

# Convert to new format
new_dict = {param["name"]: param["type"] for param in old_list}
new_params = json.dumps(new_dict)

print(new_params)
# Output: '{"nums": "list[int]", "target": "int"}'
```
