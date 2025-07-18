# Rate Limiting Documentation

## Overview

The Kalori Makanan API now includes comprehensive rate limiting to ensure fair usage and protect against abuse. The system uses API key authentication with a sliding window algorithm for accurate rate tracking.

## Rate Limits

Each API key is subject to the following limits:

| Time Period | Limit | Notes |
|-------------|-------|-------|
| Per Minute | 10 requests | ~0.17 req/s |
| Per Hour | 200 requests | ~0.056 req/s |
| Per Day | 500 requests | ~0.006 req/s |

**Additional Constraints:**
- Maximum 5 concurrent requests across all API keys
- Maximum 30 API keys supported (free tier on Render.com)

## Database Schema

The rate limiting system uses three tables in the Turso database:

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### API Keys Table
```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    key_hash TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Rate Limit Logs Table
```sql
CREATE TABLE rate_limit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    endpoint TEXT,
    FOREIGN KEY (api_key_id) REFERENCES api_keys(id) ON DELETE CASCADE
);
```

## API Key Management

### Creating a Test User and API Key

```bash
# Create test user (development only)
curl -X POST http://localhost:8000/api/create-test-user
```

Response:
```json
{
  "api_key": "kkm_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890",
  "message": "API key created successfully. Store this key securely as it won't be shown again."
}
```

### Creating API Keys for Existing Users

```bash
# Create API key for a specific user
curl -X POST http://localhost:8000/api/create-api-key \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "name": "Production API Key"
  }'
```

## Using the API

### Authentication

Include your API key in the `X-API-Key` header for all requests:

```bash
curl http://localhost:8000/foods/search?name=nasi \
  -H "X-API-Key: kkm_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890"
```

### Python Example

```python
import requests

API_KEY = "kkm_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890"
BASE_URL = "http://localhost:8000"

headers = {"X-API-Key": API_KEY}

# Search for foods
response = requests.get(
    f"{BASE_URL}/foods/search",
    params={"name": "nasi goreng"},
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(f"Found {data['total']} foods")
elif response.status_code == 429:
    print("Rate limit exceeded!")
    print(f"Retry after: {response.headers.get('Retry-After')} seconds")
```

### JavaScript/Fetch Example

```javascript
const API_KEY = 'kkm_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890';
const BASE_URL = 'http://localhost:8000';

async function searchFoods(query) {
  try {
    const response = await fetch(
      `${BASE_URL}/foods/search?name=${encodeURIComponent(query)}`,
      {
        headers: {
          'X-API-Key': API_KEY
        }
      }
    );

    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After');
      console.error(`Rate limit exceeded. Retry after ${retryAfter} seconds`);
      return null;
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error searching foods:', error);
    return null;
  }
}
```

## Rate Limit Headers

The API returns the following headers with each response:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit-Minute` | Total requests allowed per minute |
| `X-RateLimit-Remaining-Minute` | Requests remaining this minute |
| `X-RateLimit-Limit-Hour` | Total requests allowed per hour |
| `X-RateLimit-Remaining-Hour` | Requests remaining this hour |
| `X-RateLimit-Limit-Day` | Total requests allowed per day |
| `X-RateLimit-Remaining-Day` | Requests remaining today |

When rate limit is exceeded:
- `Retry-After`: Number of seconds to wait before retrying

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "API key required"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded: 10 requests per minute"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Server overloaded. Maximum concurrent requests exceeded."
}
```

## Checking Rate Limit Status

You can check your current rate limit status:

```bash
curl http://localhost:8000/api/rate-limit-status \
  -H "X-API-Key: kkm_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890"
```

Response:
```json
{
  "status": "active",
  "user": {
    "email": "test@example.com",
    "name": "Test User"
  },
  "limits": {
    "per_minute": {
      "limit": 10,
      "used": 3,
      "remaining": 7
    },
    "per_hour": {
      "limit": 200,
      "used": 15,
      "remaining": 185
    },
    "per_day": {
      "limit": 500,
      "used": 45,
      "remaining": 455
    }
  }
}
```

## Frontend Integration

Since the login functionality will be in the frontend repository but shares the same Turso database:

1. The frontend can create users in the `users` table
2. After user registration/login, the frontend can call the API to create an API key
3. The frontend should securely store the API key (e.g., in encrypted local storage)
4. Include the API key in all requests to the backend API

Example frontend flow:
```javascript
// After successful user registration/login
const createApiKey = async (userId) => {
  const response = await fetch('/api/create-api-key', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      user_id: userId,
      name: 'Web App Key'
    })
  });
  
  const data = await response.json();
  // Securely store data.api_key
  localStorage.setItem('api_key', encrypt(data.api_key));
};
```

## Maintenance

### Cleaning Up Old Logs

To prevent database bloat, periodically clean up old rate limit logs:

```bash
# Clean up logs older than 7 days
curl -X POST http://localhost:8000/api/cleanup-logs?days_to_keep=7
```

**Note:** In production, this should be a scheduled job, not an API endpoint.

## Testing

Run the example script to test the rate limiting:

```bash
python example_usage.py
```

This will:
1. Create a test user and API key
2. Make authenticated requests
3. Show rate limit headers
4. Demonstrate rate limiting behavior

## Security Considerations

1. **API Key Storage**: Never commit API keys to version control
2. **HTTPS**: Always use HTTPS in production to protect API keys in transit
3. **Key Rotation**: Implement key rotation for production use
4. **Monitoring**: Monitor for unusual patterns that might indicate abuse

## Algorithm Details

The system uses a **sliding window algorithm** for accurate rate limiting:

- For each request, it counts all requests within the time window (60s, 3600s, or 86400s)
- If the count exceeds the limit, the request is rejected
- This provides more accurate limiting than fixed window algorithms

## Deployment Notes

When deploying to Render.com (free tier):
- The in-memory concurrent request tracker will reset on each deployment
- Rate limit logs persist in Turso database
- Consider implementing a cleanup job for old logs
- Monitor database size to stay within Turso limits

## Troubleshooting

### Common Issues

1. **"API key required" error**
   - Ensure you're including the `X-API-Key` header
   - Check that the header name is exactly `X-API-Key` (case-sensitive)

2. **"Invalid API key" error**
   - Verify the API key is correct and complete
   - Check if the API key is active in the database
   - Ensure the associated user exists

3. **Rate limit exceeded immediately**
   - Check if old requests are being counted
   - Verify the database time is synchronized
   - Consider cleaning up old logs

### Debug Commands

```bash
# Check database tables
sqlite3 your-database.db "SELECT name FROM sqlite_master WHERE type='table';"

# View recent rate limit logs
sqlite3 your-database.db "SELECT * FROM rate_limit_logs ORDER BY timestamp DESC LIMIT 10;"

# Check API key status
sqlite3 your-database.db "SELECT * FROM api_keys WHERE key_hash='...';"
```
