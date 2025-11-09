# Submission API Documentation

## Overview
The Submission API allows authenticated users to submit code solutions for problems and track their submission history.

## Endpoints

### 1. Submit Code
**POST** `/submissions/submit`

Submit code for a problem. Runs against **all** test cases including hidden ones.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "problem_id": 1,
  "code": "def solution(nums):\n    return sorted(nums)",
  "language": "python"
}
```

**Response:**
```json
{
  "solution_id": 123,
  "success": true,
  "status": "accepted",
  "message": "Accepted! All 10 test cases passed.",
  "test_results": [
    {
      "test_case_id": 1,
      "input": "[3, 1, 2]",
      "expected_output": "[1, 2, 3]",
      "actual_output": "[1, 2, 3]",
      "passed": true,
      "error": null,
      "execution_time": 0.023,
      "is_hidden": false
    }
  ],
  "total_tests": 10,
  "passed_tests": 10,
  "execution_time": 0.234
}
```

**Status Values:**
- `accepted` - All test cases passed
- `wrong_answer` - Failed one or more test cases
- `time_limit_exceeded` - Execution took too long
- `runtime_error` - Code crashed during execution
- `compilation_error` - Code failed to compile

---

### 2. Get My Submissions
**GET** `/submissions/me?skip=0&limit=100`

Get all submissions for the currently authenticated user.

**Authentication Required:** Yes

**Query Parameters:**
- `skip` (optional): Number of records to skip for pagination (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100, max: 1000)

**Response:**
```json
[
  {
    "id": 123,
    "problem_id": 1,
    "language": "python",
    "status": "accepted",
    "created_at": "2025-11-09T10:30:00Z"
  }
]
```

---

### 3. Get Problem Submissions
**GET** `/submissions/problem/{problem_id}?skip=0&limit=100`

Get all submissions for a specific problem by the current user.

**Authentication Required:** Yes

**Path Parameters:**
- `problem_id`: ID of the problem

**Query Parameters:**
- `skip` (optional): Number of records to skip for pagination
- `limit` (optional): Maximum number of records to return

**Response:** Same as "Get My Submissions"

---

### 4. Get Submission Details
**GET** `/submissions/{solution_id}`

Get detailed information about a specific submission.

**Authentication Required:** Yes (can only view own submissions)

**Path Parameters:**
- `solution_id`: ID of the submission

**Response:**
```json
{
  "id": 123,
  "user_id": 456,
  "problem_id": 1,
  "code": "def solution(nums):\n    return sorted(nums)",
  "language": "python",
  "status": "accepted",
  "created_at": "2025-11-09T10:30:00Z"
}
```

---

## Differences: Run Code vs Submit Code

| Feature | Run Code (`/compile_problem`) | Submit Code (`/submissions/submit`) |
|---------|-------------------------------|-------------------------------------|
| **Test Cases** | Only public test cases | All test cases (public + hidden) |
| **Authentication** | Not required | Required |
| **Saves to DB** | No | Yes (creates Solution record) |
| **Purpose** | Testing/debugging | Official submission for evaluation |
| **Stops on Failure** | Continues all public tests | Stops on first failure |

---

## Database Schema

### Solution Model
```python
class Solution(Base):
    id = Integer (Primary Key)
    user_id = Integer (Foreign Key -> users.id)
    problem_id = Integer (Foreign Key -> problems.id)
    code = Text
    language = String(50)
    status = Enum(SubmissionStatus)
    created_at = DateTime
```

### SubmissionStatus Enum
- `ACCEPTED`
- `WRONG_ANSWER`
- `TIME_LIMIT_EXCEEDED`
- `RUNTIME_ERROR`
- `COMPILATION_ERROR`

---

## Usage Example (Frontend)

```javascript
// Submit code
const submitCode = async (problemId, code, language) => {
  const response = await apiClient.post('/submissions/submit', {
    problem_id: problemId,
    code: code,
    language: language
  });
  
  return response.data;
};

// Get submission history
const getMySubmissions = async (skip = 0, limit = 100) => {
  const response = await apiClient.get('/submissions/me', {
    params: { skip, limit }
  });
  
  return response.data;
};

// Get problem-specific submissions
const getProblemSubmissions = async (problemId) => {
  const response = await apiClient.get(`/submissions/problem/${problemId}`);
  return response.data;
};
```
