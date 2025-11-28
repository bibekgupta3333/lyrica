# Authentication API Quick Reference

**Quick reference guide for Lyrica authentication endpoints**

## Base URL

```
http://localhost:8000/api/v1/auth
```

---

## 📝 User Registration

### Register a New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPassword123!",
    "full_name": "John Doe",
    "username": "johndoe"
  }'
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "username": "johndoe",
  "is_active": true,
  "is_verified": false,
  "role": "user",
  "created_at": "2025-11-28T...",
  "updated_at": "2025-11-28T..."
}
```

---

## 🔑 User Login

### Login (OAuth2 Format)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=StrongPassword123!"
```

### Login (JSON Format)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPassword123!"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

## 🔄 Token Refresh

### Refresh Access Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

## 👤 User Profile

### Get Current User Profile

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "username": "johndoe",
  "is_active": true,
  "is_verified": false,
  "role": "user",
  "created_at": "2025-11-28T...",
  "updated_at": "2025-11-28T..."
}
```

### Update User Profile

```bash
curl -X PUT http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith",
    "username": "johnsmith"
  }'
```

### Change Password

```bash
curl -X POST http://localhost:8000/api/v1/auth/me/password \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPassword123!",
    "new_password": "NewPassword456!"
  }'
```

---

## 🔐 API Keys

### Create API Key

```bash
curl -X POST http://localhost:8000/api/v1/auth/api-keys \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Mobile App",
    "expires_days": 365
  }'
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "name": "My Mobile App",
  "key_prefix": "lyr_abcd",
  "api_key": "lyr_abcdef1234567890abcdef1234567890",
  "created_at": "2025-11-28T...",
  "expires_at": "2026-11-28T...",
  "last_used_at": null,
  "is_active": true
}
```

⚠️ **Important**: Save the full `api_key` value - it's only shown once!

### List API Keys

```bash
curl http://localhost:8000/api/v1/auth/api-keys \
  -H "Authorization: Bearer <access_token>"
```

### Revoke API Key

```bash
curl -X DELETE http://localhost:8000/api/v1/auth/api-keys/<key_id> \
  -H "Authorization: Bearer <access_token>"
```

---

## 🧪 Testing & Status

### Test Authentication

```bash
# With JWT token
curl http://localhost:8000/api/v1/auth/test-auth \
  -H "Authorization: Bearer <access_token>"

# With API key
curl http://localhost:8000/api/v1/auth/test-auth \
  -H "X-API-Key: lyr_abcdef1234567890abcdef1234567890"
```

### Get Auth Status

```bash
curl http://localhost:8000/api/v1/auth/status \
  -H "Authorization: Bearer <access_token>"
```

**Response (200 OK):**
```json
{
  "authenticated": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "user"
  },
  "permissions": ["read:own", "write:own"]
}
```

---

## 🔒 Using Authentication in Requests

### With JWT Token (Recommended for Web)

```bash
curl http://localhost:8000/api/v1/lyrics/ \
  -H "Authorization: Bearer <access_token>"
```

### With API Key (Recommended for Mobile)

```bash
curl http://localhost:8000/api/v1/lyrics/ \
  -H "X-API-Key: lyr_abcdef1234567890abcdef1234567890"
```

---

## ⚠️ Error Responses

### 400 Bad Request

```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden

```json
{
  "detail": "Inactive user"
}
```

### 429 Too Many Requests

```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Try again in 30 seconds.",
  "retry_after": 30
}
```

**Headers:**
- `X-RateLimit-Limit: 60`
- `X-RateLimit-Remaining: 0`
- `X-RateLimit-Reset: 1701234567`
- `Retry-After: 30`

---

## 🎯 Common Workflows

### Complete Registration & Login Flow

```bash
# 1. Register
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "new@user.com",
    "password": "SecurePass123!",
    "full_name": "New User"
  }' | jq -r '.id')

# 2. Login
ACCESS_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=new@user.com&password=SecurePass123!" \
  | jq -r '.access_token')

# 3. Access protected resource
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### API Key Workflow for Mobile Apps

```bash
# 1. Login with user credentials
TOKENS=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=user@example.com&password=password")

ACCESS_TOKEN=$(echo $TOKENS | jq -r '.access_token')

# 2. Create API key
API_KEY=$(curl -s -X POST http://localhost:8000/api/v1/auth/api-keys \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Mobile App",
    "expires_days": 365
  }' | jq -r '.api_key')

# 3. Use API key for subsequent requests
curl http://localhost:8000/api/v1/lyrics/ \
  -H "X-API-Key: $API_KEY"
```

---

## 📚 Related Documentation

- [Full API Reference](API_REFERENCE.md)
- [Agent System Guide](AGENT_SYSTEM_GUIDE.md)
- [RAG API Quick Reference](RAG_API_QUICK_REFERENCE.md)
- [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md)

---

**Last Updated**: November 28, 2025  
**API Version**: 1.0.0
