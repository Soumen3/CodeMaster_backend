# Test Case Data Structure Documentation

## Overview

Test cases in CodeMaster are stored as text fields in the database, allowing flexibility for different input/output formats. This document describes the recommended structure and best practices for storing test case data.

---

## Database Schema

### TestCase Table Structure

```sql
CREATE TABLE test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL,
    input_data TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    is_hidden BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
);
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key, auto-incrementing |
| `problem_id` | Integer | Foreign key to problems table |
| `input_data` | Text | Input for the test case (see formats below) |
| `expected_output` | Text | Expected output for the test case |
| `is_hidden` | Boolean | Whether test case is visible to users (false = public, true = hidden) |

---

## Input/Output Data Formats

### Recommended Format: JSON

For maximum flexibility and ease of parsing, we recommend storing test case data as **JSON strings**.

#### Example 1: Simple Single Value Input

```json
// Problem: Double a Number
// Input Data:
{
  "n": 5
}

// Expected Output:
{
  "result": 10
}
```

#### Example 2: Multiple Input Parameters

```json
// Problem: Add Two Numbers
// Input Data:
{
  "a": 10,
  "b": 20
}

// Expected Output:
{
  "result": 30
}
```

#### Example 3: Array/List Input

```json
// Problem: Find Maximum in Array
// Input Data:
{
  "arr": [1, 5, 3, 9, 2]
}

// Expected Output:
{
  "result": 9
}
```

#### Example 4: Complex Data Structures

```json
// Problem: Graph Traversal
// Input Data:
{
  "nodes": 5,
  "edges": [[0,1], [1,2], [2,3], [3,4]],
  "start": 0
}

// Expected Output:
{
  "path": [0, 1, 2, 3, 4]
}
```

#### Example 5: String Manipulation

```json
// Problem: Reverse String
// Input Data:
{
  "text": "hello world"
}

// Expected Output:
{
  "result": "dlrow olleh"
}
```

---

### Alternative Format: Plain Text (Line-Separated)

For simple problems, you can use newline-separated values.

#### Example: Two Sum Problem

```
Input Data:
[2, 7, 11, 15]
9

Expected Output:
[0, 1]
```

#### Format Rules:
- Each input parameter on a new line
- Arrays represented as comma-separated values in brackets
- Output follows the same format

---

### Alternative Format: Space-Separated (Competitive Programming Style)

Common in competitive programming platforms.

#### Example: Add Two Numbers

```
Input Data:
5 10

Expected Output:
15
```

#### Example: Array Processing

```
Input Data:
5
1 2 3 4 5

Expected Output:
15
```

(First line is array length, second line is array elements)

---

## Pydantic Schemas

### TestCaseBase Schema

```python
class TestCaseBase(BaseModel):
    """Base schema for test cases"""
    input_data: str
    expected_output: str
    is_hidden: bool = False
```

### TestCaseCreate Schema

```python
class TestCaseCreate(TestCaseBase):
    """Schema for creating a new test case"""
    problem_id: int
```

**Usage Example:**

```python
# JSON format
test_case = TestCaseCreate(
    problem_id=1,
    input_data='{"n": 5}',
    expected_output='{"result": 10}',
    is_hidden=False
)

# Plain text format
test_case = TestCaseCreate(
    problem_id=2,
    input_data='5 10',
    expected_output='15',
    is_hidden=False
)
```

### TestCaseResponse Schema

```python
class TestCaseResponse(TestCaseBase):
    """Schema for test case response"""
    id: int
    problem_id: int

    class Config:
        from_attributes = True
```

**Response Example:**

```json
{
  "id": 1,
  "problem_id": 1,
  "input_data": "{\"n\": 5}",
  "expected_output": "{\"result\": 10}",
  "is_hidden": false
}
```

---

## API Examples

### Creating a Test Case

**Request:**
```bash
POST /problems/1/testcases
Content-Type: application/json

{
  "problem_id": 1,
  "input_data": "{\"arr\": [1, 2, 3, 4, 5]}",
  "expected_output": "{\"result\": 15}",
  "is_hidden": false
}
```

**Response:**
```json
{
  "id": 1,
  "problem_id": 1,
  "input_data": "{\"arr\": [1, 2, 3, 4, 5]}",
  "expected_output": "{\"result\": 15}",
  "is_hidden": false
}
```

### Getting Test Cases for a Problem

**Request:**
```bash
GET /problems/1/testcases?include_hidden=false
```

**Response:**
```json
[
  {
    "id": 1,
    "problem_id": 1,
    "input_data": "{\"arr\": [1, 2, 3]}",
    "expected_output": "{\"result\": 6}",
    "is_hidden": false
  },
  {
    "id": 2,
    "problem_id": 1,
    "input_data": "{\"arr\": [5, 10, 15]}",
    "expected_output": "{\"result\": 30}",
    "is_hidden": false
  }
]
```

---

## Best Practices

### 1. Use JSON for Complex Data

✅ **Recommended:**
```json
{
  "matrix": [[1,2], [3,4]],
  "target": 5
}
```

❌ **Not Recommended:**
```
[[1,2], [3,4]]
5
```

### 2. Consistent Formatting

- Use the same format for all test cases of a problem
- Don't mix JSON and plain text for the same problem
- Maintain consistent key names

### 3. Hidden Test Cases

```python
# Public test cases (visible to users during development)
TestCaseCreate(
    problem_id=1,
    input_data='{"n": 5}',
    expected_output='{"result": 10}',
    is_hidden=False  # Users can see this
)

# Hidden test cases (used during final submission evaluation)
TestCaseCreate(
    problem_id=1,
    input_data='{"n": 1000000}',
    expected_output='{"result": 2000000}',
    is_hidden=True  # Users cannot see this until after submission
)
```

### 4. Edge Cases

Always include edge case test cases:

```python
# Edge case: Empty array
TestCaseCreate(
    problem_id=1,
    input_data='{"arr": []}',
    expected_output='{"result": 0}',
    is_hidden=False
)

# Edge case: Single element
TestCaseCreate(
    problem_id=1,
    input_data='{"arr": [42]}',
    expected_output='{"result": 42}',
    is_hidden=False
)

# Edge case: Negative numbers
TestCaseCreate(
    problem_id=1,
    input_data='{"arr": [-1, -2, -3]}',
    expected_output='{"result": -6}',
    is_hidden=False
)
```

### 5. Data Validation

Before storing, validate that:
- JSON is properly formatted (if using JSON)
- Input/output can be parsed
- Data types match problem requirements

```python
import json

def validate_test_case_json(test_case_data: str) -> bool:
    """Validate that test case data is valid JSON"""
    try:
        json.loads(test_case_data)
        return True
    except json.JSONDecodeError:
        return False

# Usage
if validate_test_case_json(input_data) and validate_test_case_json(expected_output):
    # Create test case
    pass
```

---

## Code Runner Integration

### Parsing Test Cases

When executing code, parse the test case data:

```python
import json

def run_test_case(code: str, test_case: TestCase) -> bool:
    """Execute code with test case and check output"""
    
    # Parse input data
    input_json = json.loads(test_case.input_data)
    expected_json = json.loads(test_case.expected_output)
    
    # Execute user code with input
    actual_output = execute_code(code, input_json)
    
    # Compare with expected output
    return actual_output == expected_json
```

### Example Test Execution

```python
# Test Case
input_data = '{"arr": [1, 2, 3, 4, 5]}'
expected_output = '{"result": 15}'

# User's submitted code
user_code = """
def solution(arr):
    return {"result": sum(arr)}
"""

# Parse and execute
input_params = json.loads(input_data)  # {"arr": [1, 2, 3, 4, 5]}
result = solution(**input_params)       # {"result": 15}
expected = json.loads(expected_output)  # {"result": 15}

assert result == expected  # Test passes!
```

---

## Database Relationships

### Problem → TestCases (One-to-Many)

```python
# Problem model
class Problem(Base):
    __tablename__ = "problems"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    # ... other fields
    
    # Relationship
    test_cases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")

# TestCase model
class TestCase(Base):
    __tablename__ = "test_cases"
    id = Column(Integer, primary_key=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"))
    # ... other fields
    
    # Relationship
    problem = relationship("Problem", back_populates="test_cases")
```

**Cascade Behavior:**
- When a problem is deleted, all its test cases are automatically deleted
- This prevents orphaned test cases in the database

---

## Storage Considerations

### Text Field Size

- **SQLite:** `TEXT` type has no practical size limit (up to 1GB)
- **PostgreSQL:** `TEXT` type is unlimited
- **MySQL:** `TEXT` can store up to 65,535 bytes

For very large inputs (e.g., big matrices), consider:
1. Using `MEDIUMTEXT` (MySQL) or equivalent
2. Storing large test data in files and keeping file paths in database
3. Compressing large inputs

### Indexing

Test cases don't need complex indexing since they're always queried by `problem_id`:

```sql
CREATE INDEX idx_test_cases_problem_id ON test_cases(problem_id);
```

This index is automatically created due to the foreign key constraint.

---

## Example: Complete Problem with Test Cases

```python
# Create a problem
problem = ProblemCreate(
    title="Two Sum",
    description="Find two numbers that add up to target",
    difficulty=Difficulty.EASY
)

# Public test cases (users can see)
test_cases = [
    TestCaseCreate(
        problem_id=1,
        input_data='{"nums": [2, 7, 11, 15], "target": 9}',
        expected_output='{"indices": [0, 1]}',
        is_hidden=False
    ),
    TestCaseCreate(
        problem_id=1,
        input_data='{"nums": [3, 2, 4], "target": 6}',
        expected_output='{"indices": [1, 2]}',
        is_hidden=False
    ),
]

# Hidden test cases (for final evaluation)
hidden_test_cases = [
    TestCaseCreate(
        problem_id=1,
        input_data='{"nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "target": 19}',
        expected_output='{"indices": [8, 9]}',
        is_hidden=True
    ),
    TestCaseCreate(
        problem_id=1,
        input_data='{"nums": [-1, -2, -3, -4, -5], "target": -8}',
        expected_output='{"indices": [2, 4]}',
        is_hidden=True
    ),
]
```

---

## Summary

### Key Points:

1. **Storage Format**: Use JSON strings for flexibility and ease of parsing
2. **Fields**: `input_data` (TEXT), `expected_output` (TEXT), `is_hidden` (BOOLEAN)
3. **Relationships**: Many test cases per problem, cascade delete
4. **Best Practice**: Always include both public and hidden test cases
5. **Validation**: Validate JSON format before storing
6. **Parsing**: Use `json.loads()` to parse data before code execution

This structure provides maximum flexibility while maintaining simplicity and performance.
