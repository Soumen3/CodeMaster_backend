# Authentication System Documentation

## Overview
The CodeMaster backend uses JWT (JSON Web Tokens) for API authentication. Users authenticate via OAuth (Google/GitHub), and receive a JWT token that must be included in subsequent API requests.

## Authentication Flow

### 1. OAuth Login (Google/GitHub)
```
User → OAuth Provider → Backend Callback → JWT Token → Frontend
```

**Steps:**
1. User clicks "Login with Google/GitHub"
2. Redirected to OAuth provider
3. After authorization, redirected back to `/auth/{provider}/callback`
4. Backend creates/updates user in database
5. Backend generates JWT token
6. User data and JWT token sent to frontend

### 2. API Authentication
All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## JWT Token Structure

**Payload:**
```json
{
  "sub": 123,  // User ID
  "exp": 1699999999  // Expiration timestamp
}
```

**Configuration:**
- Algorithm: HS256
- Expiration: 30 days (default)
- Secret Key: Set via `SECRET_KEY` environment variable

## Security Functions

### `create_access_token(data, expires_delta)`
Creates a new JWT token.

**Args:**
- `data` (dict): Data to encode in token
- `expires_delta` (Optional[timedelta]): Custom expiration time

**Returns:**
- JWT token string

**Example:**
```python
from datetime import timedelta
token = create_access_token(
    data={"sub": user.id},
    expires_delta=timedelta(days=30)
)
```

### `decode_access_token(token)`
Decodes and validates a JWT token.

**Args:**
- `token` (str): JWT token string

**Returns:**
- Decoded payload dictionary

**Raises:**
- `HTTPException(401)`: If token is invalid or expired

### `get_current_user(credentials, db)`
Dependency function to get authenticated user from request.

**Usage in Routes:**
```python
from ..core.security import get_current_user
from ..database.models import User

@router.get("/protected-endpoint")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    return {"user_id": current_user.id}
```

**Behavior:**
- Extracts Bearer token from Authorization header
- Decodes and validates token
- Fetches user from database
- Returns User object
- Raises 401 error if authentication fails

### `get_current_user_optional(credentials, db)`
Optional authentication - returns None if no token provided.

**Usage:**
```python
@router.get("/optional-auth-endpoint")
async def optional_auth_route(
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    if current_user:
        return {"message": f"Hello {current_user.name}"}
    else:
        return {"message": "Hello guest"}
```

## Frontend Integration

### Storing the Token
After OAuth login, store the JWT token:

```javascript
// In AuthContext or similar
const handleAuthSuccess = (data) => {
  localStorage.setItem('token', data.token);
  localStorage.setItem('user', JSON.stringify({
    id: data.id,
    email: data.email,
    name: data.name,
    avatar_url: data.avatar_url
  }));
};
```

### Making Authenticated Requests

```javascript
// Using axios or fetch
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
});

// Add token to all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Example: Submit code
const submitCode = async (problemId, code, language) => {
  const response = await apiClient.post('/submissions/submit', {
    problem_id: problemId,
    code: code,
    language: language
  });
  return response.data;
};
```

### Handling 401 Errors

```javascript
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## Environment Variables

Required in `.env`:

```env
# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 days

# OAuth Providers
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# URLs
FRONTEND_URL=http://localhost:5173
BACKEND_HOST=http://localhost:8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/codemaster
```

## Protected Endpoints

The following endpoints require authentication:

### Submissions
- `POST /submissions/submit` - Submit code solution
- `GET /submissions/me` - Get user's submissions
- `GET /submissions/problem/{problem_id}` - Get problem-specific submissions
- `GET /submissions/{solution_id}` - Get submission details

### Future Protected Endpoints
- User profile management
- Problem bookmarking/favorites
- Discussion forum posts
- etc.

## Security Best Practices

1. **Secret Key**: Use a strong, random secret key in production
   ```bash
   # Generate a secure secret key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **HTTPS Only**: In production, use HTTPS to prevent token interception

3. **Token Expiration**: Tokens expire after 30 days by default. Implement refresh token mechanism for better security.

4. **Token Storage**: 
   - ✅ Store in localStorage (simple, but vulnerable to XSS)
   - ✅ Store in httpOnly cookies (more secure, but requires CORS configuration)

5. **Validation**: All protected endpoints automatically validate tokens via the `get_current_user` dependency

## Testing Authentication

### Using curl
```bash
# 1. Login via OAuth (use browser)
# 2. Get token from response
# 3. Use token in API calls

curl -X POST http://localhost:8000/submissions/submit \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_id": 1,
    "code": "def solution(nums): return sorted(nums)",
    "language": "python"
  }'
```

### Using Postman
1. Set Authorization type to "Bearer Token"
2. Paste JWT token in the Token field
3. Make request to protected endpoint

## Troubleshooting

### Error: "Could not validate credentials"
**Causes:**
- Token expired
- Invalid token format
- Wrong SECRET_KEY
- Token not included in request

**Solutions:**
- Check token is included in Authorization header as `Bearer <token>`
- Verify SECRET_KEY matches between token creation and validation
- Re-authenticate if token expired

### Error: "Import jose could not be resolved"
**Solution:**
```bash
pip install python-jose[cryptography]
```

### Token Not Working After Server Restart
**Cause:** If SECRET_KEY changes, all existing tokens become invalid

**Solution:** Keep SECRET_KEY consistent in environment variables
