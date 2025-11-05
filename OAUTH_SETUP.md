# OAuth Setup Guide

This guide walks you through setting up OAuth authentication for Google and GitHub.

## Google OAuth Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create a New Project** (or select existing)
   - Click "Select a project" → "New Project"
   - Name it (e.g., "CodeMaster")

3. **Enable Google+ API**
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google+ API" and enable it

4. **Create OAuth Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Configure consent screen if prompted
   - Application type: "Web application"
   - Name: "CodeMaster Web Client"

5. **Configure Authorized Redirect URIs**
   ```
   http://localhost:8000/auth/google/callback
   http://localhost:5173/auth/success
   ```
   Add production URLs when deploying.

6. **Copy Credentials**
   - Copy the Client ID and Client Secret
   - Add them to your `.env` file:
   ```bash
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

## GitHub OAuth Setup

1. **Go to GitHub Developer Settings**
   - Visit: https://github.com/settings/developers
   - Or: Settings → Developer settings → OAuth Apps

2. **Register a New OAuth Application**
   - Click "New OAuth App"
   - Fill in the details:
     - **Application name**: CodeMaster
     - **Homepage URL**: `http://localhost:5173`
     - **Authorization callback URL**: `http://localhost:8000/auth/github/callback`

3. **Generate Client Secret**
   - After creating the app, generate a new client secret
   - Copy both the Client ID and Client Secret immediately

4. **Add to Environment Variables**
   - Add them to your `.env` file:
   ```bash
   GITHUB_CLIENT_ID=your-github-client-id
   GITHUB_CLIENT_SECRET=your-github-client-secret
   ```

## Environment Configuration

Complete `.env` file example:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdef123456

# GitHub OAuth
GITHUB_CLIENT_ID=Iv1.abc123def456
GITHUB_CLIENT_SECRET=abc123def456ghi789

# URLs
BACKEND_HOST=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/codemaster
```

## Testing OAuth Flow

1. **Start the backend server**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test the flow**:
   - Visit `http://localhost:5173/login`
   - Click "Continue with Google" or "Continue with GitHub"
   - Complete the OAuth flow
   - You should be redirected to `/profile` with your user info

## Troubleshooting

### Google OAuth Issues

- **Error: redirect_uri_mismatch**
  - Make sure the redirect URI in Google Console exactly matches `http://localhost:8000/auth/google/callback`
  - No trailing slashes!

- **Error: access_denied**
  - User canceled the OAuth flow
  - Or app is in testing mode and user email not added to test users

### GitHub OAuth Issues

- **Error: redirect_uri_mismatch**
  - Verify callback URL in GitHub app settings is `http://localhost:8000/auth/github/callback`

- **No email returned**
  - User's GitHub email might be private
  - App will attempt to fetch from `/user/emails` endpoint
  - Ensure OAuth scope includes `user:email`

### General Issues

- **CORS errors**: Check `BACKEND_HOST` and `FRONTEND_URL` in `.env`
- **Database errors**: Verify `DATABASE_URL` is correct and database is running
- **Missing credentials**: Make sure all OAuth credentials are in `.env` file

## Production Deployment

When deploying to production:

1. **Update redirect URIs** in Google/GitHub OAuth apps to your production URLs
2. **Update environment variables** with production URLs:
   ```bash
   BACKEND_HOST=https://api.yourapp.com
   FRONTEND_URL=https://yourapp.com
   ```
3. **Use HTTPS** for all OAuth flows in production
4. **Enable proper CORS** settings for your production domain
5. **Secure your secrets** using environment variable management (never commit `.env`)

## Security Notes

- Never commit `.env` file to version control
- Use strong, random client secrets
- In production, consider using HTTP-only cookies instead of localStorage
- Implement JWT validation for id_tokens
- Add rate limiting to OAuth endpoints
- Monitor for suspicious OAuth activity
