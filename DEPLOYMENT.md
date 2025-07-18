# Deployment Guide - Render.com

This guide walks you through deploying the Kalori Makanan API with rate limiting to Render.com.

## Prerequisites

- GitHub account with your repository
- Render.com account (free tier works)
- Turso database set up with credentials

## Step 1: Prepare Your Repository

1. **Ensure all files are committed**
```bash
git add .
git commit -m "Add rate limiting system"
git push origin main
```

2. **Required files in your repo:**
- `app/` directory with all Python files
- `requirements.txt`
- `render.yaml` (optional but recommended)
- `setup_rate_limiting.py`
- `RATE_LIMITING.md`

## Step 2: Deploy to Render

### Option A: Using Render Dashboard (Recommended)

1. **Go to [render.com](https://render.com) and log in**

2. **Create a new Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Choose your `kalori-makanan-kkm` repository

3. **Configure the service:**
   - **Name**: `kalori-makanan-api`
   - **Branch**: `main`
   - **Root Directory**: Leave blank (root of repo)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables** (in Render dashboard):
   ```
   TURSO_DATABASE_URL=libsql://your-database-url.turso.io
   TURSO_DATABASE_TOKEN=your_database_token
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete (usually 2-5 minutes)

### Option B: Using render.yaml (Auto-deploy)

If you have `render.yaml` in your repo:

1. **Go to Render dashboard**
2. **Click "New +" → "Blueprint"**
3. **Connect your repository**
4. **Render will automatically read `render.yaml`**

## Step 3: Set Up Rate Limiting Tables

After deployment, you need to create the database tables:

### Method 1: Using Render Shell (Recommended)

1. **Go to your deployed service in Render dashboard**
2. **Click "Shell" tab**
3. **Run the setup script:**
```bash
python setup_rate_limiting.py
```
4. **Choose 'y' when asked to create a test user**
5. **Note down the API key provided**

### Method 2: Using local script with production database

1. **Update your local `.env` to point to production database**
2. **Run locally:**
```bash
python setup_rate_limiting.py
```
3. **Change `.env` back to local database**

## Step 4: Test Your Deployment

1. **Get your Render URL** (something like `https://kalori-makanan-api.onrender.com`)

2. **Test the health endpoint** (no API key required):
```bash
curl https://your-app.onrender.com/health
```

3. **Create a test user and API key:**
```bash
curl -X POST https://your-app.onrender.com/api/create-test-user
```

4. **Test authenticated endpoints:**
```bash
# Use the API key from step 3
curl "https://your-app.onrender.com/foods/search?name=nasi" \
  -H "X-API-Key: your_api_key_here"
```

5. **Check rate limit status:**
```bash
curl https://your-app.onrender.com/api/rate-limit-status \
  -H "X-API-Key: your_api_key_here"
```

## Step 5: Verify Everything Works

Run through this checklist:

- [ ] Health endpoint responds
- [ ] Can create test users
- [ ] API key authentication works
- [ ] Rate limiting headers are present
- [ ] All food endpoints work with API key
- [ ] Rate limits are enforced (test by making 11+ requests in a minute)
- [ ] Documentation is accessible at `/docs`

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `TURSO_DATABASE_URL` | Yes | Your Turso database URL | `libsql://db-name.turso.io` |
| `TURSO_DATABASE_TOKEN` | Yes | Database auth token | `eyJhbGci...` |
| `PORT` | No | Port (auto-set by Render) | `10000` |

## render.yaml Configuration

Create this file in your repository root:

```yaml
services:
  - type: web
    name: kalori-makanan-api
    runtime: python3
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: TURSO_DATABASE_URL
        value: libsql://your-database-url.turso.io
      - key: TURSO_DATABASE_TOKEN
        value: your_database_token
```

## Post-Deployment Setup

### 1. Set up periodic log cleanup

Add this to your deployment script or run manually:

```bash
# Clean up old logs weekly
curl -X POST https://your-app.onrender.com/api/cleanup-logs?days_to_keep=7
```

### 2. Create production API keys

For production use, create proper users instead of test users:

```bash
# This should be done through your frontend application
curl -X POST https://your-app.onrender.com/api/create-api-key \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "name": "Production Key"}'
```

## Frontend Integration

Your frontend (separate repo) can integrate with this API:

1. **Same Turso Database**: Your frontend and API share the same database
2. **User Management**: Frontend handles user registration/login
3. **API Key Request**: After login, frontend requests API key from backend
4. **API Calls**: Frontend includes API key in all requests

Example frontend flow:
```javascript
// After user logs in successfully
const response = await fetch('/api/create-api-key', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    user_id: user.id,
    name: 'Web App Key'
  })
});

const { api_key } = await response.json();
// Store securely and use in subsequent requests
```

## Monitoring and Maintenance

### 1. Monitor Usage
- Check Render logs for errors
- Monitor database size in Turso
- Track API usage patterns

### 2. Regular Maintenance
- Clean up old rate limit logs weekly
- Monitor for unusual traffic patterns
- Update dependencies regularly

### 3. Scaling Considerations
- Free tier handles ~1000 requests/day across all users
- Consider upgrading Render plan for production use
- Monitor Turso database limits

## Troubleshooting

### Common Issues

1. **"Database connection failed"**
   - Check environment variables are set correctly
   - Verify Turso database is accessible
   - Test connection from Render shell

2. **"API key required" errors**
   - Ensure tables are created (run setup script)
   - Check API key format
   - Verify headers are correct

3. **Rate limiting not working**
   - Check database tables exist
   - Verify rate_limit_logs table has data
   - Test with multiple rapid requests

4. **Service won't start**
   - Check build logs in Render
   - Verify requirements.txt is correct
   - Check Python version compatibility

### Debug Commands

From Render shell:
```bash
# Check database connection
python -c "from app.database import test_connection; print(test_connection())"

# List tables
python -c "from app.database import get_database; conn = get_database(); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); print(cursor.fetchall())"

# Check environment variables
env | grep TURSO
```

## Security Considerations

1. **Never commit API keys** to version control
2. **Use HTTPS only** in production (Render provides this)
3. **Monitor for abuse** patterns
4. **Rotate API keys** regularly
5. **Use proper authentication** for production users

## Cost Estimates

**Render Free Tier:**
- 750 hours/month (enough for 24/7 operation)
- 100GB bandwidth/month
- Automatically sleeps after 15 minutes of inactivity

**Turso Free Tier:**
- 9GB storage
- 1 billion row reads/month
- 25 million row writes/month

This should handle moderate traffic for free!

## Next Steps

1. **Set up monitoring** (optional)
2. **Create proper user management** in frontend
3. **Add more endpoints** as needed
4. **Implement caching** for better performance
5. **Add logging** for production debugging

Your API is now live and ready for production use! 🚀

## Support

- **API Documentation**: https://your-app.onrender.com/docs
- **Rate Limiting Guide**: See RATE_LIMITING.md
- **Issues**: Open GitHub issues for problems