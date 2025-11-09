# Frontend Integration Guide for Authentication & Submissions

## Overview
This guide shows how to integrate the new JWT authentication and submission system into the React frontend.

## 1. Update API Client

Update `frontend/src/services/apiClient.js`:

```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 errors (token expired/invalid)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## 2. Update Auth Context

Update `frontend/src/context/AuthContext.jsx`:

```javascript
import { createContext, useState, useEffect } from 'react';
import apiClient from '../services/apiClient';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const handleAuthSuccess = (data) => {
    // Store JWT token and user data
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify({
      id: data.id,
      email: data.email,
      name: data.name,
      avatar_url: data.avatar_url,
      provider: data.provider
    }));
    setUser({
      id: data.id,
      email: data.email,
      name: data.name,
      avatar_url: data.avatar_url,
      provider: data.provider
    });
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const verifyAuth = async () => {
    try {
      const response = await apiClient.get('/auth/me');
      return true;
    } catch (error) {
      logout();
      return false;
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      handleAuthSuccess, 
      logout,
      verifyAuth
    }}>
      {children}
    </AuthContext.Provider>
  );
};
```

## 3. Create Submission Service

Create `frontend/src/services/submissionService.js`:

```javascript
import apiClient from './apiClient';

/**
 * Submit code for a problem (runs against all test cases)
 */
export const submitCode = async (problemId, code, language) => {
  const response = await apiClient.post('/submissions/submit', {
    problem_id: problemId,
    code: code,
    language: language
  });
  return response.data;
};

/**
 * Get all submissions for the current user
 */
export const getMySubmissions = async (skip = 0, limit = 100) => {
  const response = await apiClient.get('/submissions/me', {
    params: { skip, limit }
  });
  return response.data;
};

/**
 * Get all submissions for a specific problem
 */
export const getProblemSubmissions = async (problemId, skip = 0, limit = 100) => {
  const response = await apiClient.get(`/submissions/problem/${problemId}`, {
    params: { skip, limit }
  });
  return response.data;
};

/**
 * Get details of a specific submission
 */
export const getSubmissionById = async (solutionId) => {
  const response = await apiClient.get(`/submissions/${solutionId}`);
  return response.data;
};

export default {
  submitCode,
  getMySubmissions,
  getProblemSubmissions,
  getSubmissionById
};
```

## 4. Update CodeEditor Component

Update the submit functionality in `frontend/src/components/CodeEditor.jsx`:

```javascript
import { submitCode } from '../services/submissionService';
import { useAuth } from '../hooks/useAuth';

const CodeEditor = ({ problem }) => {
  const { user } = useAuth();
  // ... existing code ...

  const handleSubmit = async () => {
    if (!user) {
      alert('Please login to submit code');
      return;
    }

    setIsRunning(true);
    setOutput('');
    setResultTab('result');

    try {
      const result = await submitCode(problem.id, code, language);
      
      // Format the output
      let outputText = `Status: ${result.status}\n`;
      outputText += `${result.message}\n\n`;
      outputText += `Total Tests: ${result.total_tests}\n`;
      outputText += `Passed Tests: ${result.passed_tests}\n`;
      outputText += `Execution Time: ${result.execution_time?.toFixed(3)}s\n\n`;
      
      if (result.test_results) {
        result.test_results.forEach((test, index) => {
          outputText += `Test Case ${index + 1}:\n`;
          outputText += `  Input: ${test.input}\n`;
          outputText += `  Expected: ${test.expected_output}\n`;
          outputText += `  Actual: ${test.actual_output || 'N/A'}\n`;
          outputText += `  Status: ${test.passed ? '✓ PASS' : '✗ FAIL'}\n`;
          if (test.error) {
            outputText += `  Error: ${test.error}\n`;
          }
          if (test.is_hidden) {
            outputText += `  (Hidden Test Case)\n`;
          }
          outputText += `\n`;
        });
      }
      
      outputText += `\nSubmission ID: ${result.solution_id}`;
      setOutput(outputText);
      
      // Show success/error message
      if (result.success) {
        alert('Submission Accepted! ✓');
      } else {
        alert(`Submission Failed: ${result.status}`);
      }
      
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
      setOutput(`Error: ${errorMsg}`);
      console.error('Submission error:', error);
    } finally {
      setIsRunning(false);
    }
  };

  // ... rest of component ...
};
```

## 5. Create Submissions Page

Create `frontend/src/pages/Submissions.jsx`:

```javascript
import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { getMySubmissions } from '../services/submissionService';
import { useNavigate } from 'react-router-dom';

const Submissions = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    loadSubmissions();
  }, [user]);

  const loadSubmissions = async () => {
    try {
      const data = await getMySubmissions();
      setSubmissions(data);
    } catch (error) {
      console.error('Error loading submissions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      accepted: 'text-green-500',
      wrong_answer: 'text-red-500',
      time_limit_exceeded: 'text-yellow-500',
      runtime_error: 'text-orange-500',
      compilation_error: 'text-red-600'
    };
    return colors[status] || 'text-gray-500';
  };

  const formatStatus = (status) => {
    return status.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">My Submissions</h1>
      
      {submissions.length === 0 ? (
        <div className="text-center text-gray-400 py-12">
          No submissions yet. Start solving problems!
        </div>
      ) : (
        <div className="space-y-4">
          {submissions.map((submission) => (
            <div
              key={submission.id}
              className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-indigo-500 transition-colors cursor-pointer"
              onClick={() => navigate(`/problem/${submission.problem_id}`)}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">
                    Problem #{submission.problem_id}
                  </h3>
                  <p className="text-sm text-gray-400 mt-1">
                    Language: {submission.language.toUpperCase()}
                  </p>
                  <p className="text-sm text-gray-400">
                    {new Date(submission.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="text-right">
                  <span className={`font-semibold ${getStatusColor(submission.status)}`}>
                    {formatStatus(submission.status)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Submissions;
```

## 6. Update Routes

Update `frontend/src/router/AppRouter.jsx`:

```javascript
import Submissions from '../pages/Submissions';

// Add to your routes
<Route path="/submissions" element={<Submissions />} />
```

## 7. Update Navbar

Add a link to submissions in `frontend/src/components/Navbar.jsx`:

```javascript
{user && (
  <Link to="/submissions" className="hover:text-indigo-400">
    My Submissions
  </Link>
)}
```

## Testing the Integration

### 1. Test Authentication
```javascript
// In browser console after login:
console.log(localStorage.getItem('token'));
console.log(localStorage.getItem('user'));
```

### 2. Test Submit Code
1. Login to the application
2. Go to a problem
3. Write code
4. Click Submit
5. Check the response includes `solution_id`

### 3. Test Submissions Page
1. Navigate to `/submissions`
2. Verify your submissions are listed
3. Click on a submission to go to the problem

## API Endpoints Summary

### Authentication
- `GET /auth/me` - Get current user info (requires auth)
- `GET /auth/check` - Check auth status (optional auth)

### Submissions
- `POST /submissions/submit` - Submit code (requires auth)
- `GET /submissions/me` - Get user's submissions (requires auth)
- `GET /submissions/problem/{id}` - Get problem submissions (requires auth)
- `GET /submissions/{id}` - Get submission details (requires auth)

### Code Execution (No Auth Required)
- `POST /compile_problem` - Run code against public test cases

## Key Differences

| Feature | Run Code | Submit Code |
|---------|----------|-------------|
| Endpoint | `/compile_problem` | `/submissions/submit` |
| Auth Required | ❌ No | ✅ Yes |
| Test Cases | Public only | All (public + hidden) |
| Saved to DB | ❌ No | ✅ Yes |
| Purpose | Testing/Debugging | Official submission |

## Troubleshooting

### "401 Unauthorized" Error
- Check if token exists in localStorage
- Verify token is being sent in Authorization header
- Try logging in again

### Token Not Being Sent
- Check axios interceptor is configured
- Verify apiClient is being used for all requests

### Submissions Not Loading
- Verify user is logged in
- Check network tab for request/response
- Ensure backend server is running
