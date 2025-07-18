# Kalori Makanan API 🍽️

A FastAPI application for looking up food calories, specifically focused on Malaysian and international foods. Perfect for nutrition tracking applications.

## Features

- 🔍 **Food Search**: Search for foods by name (e.g., "nasi lemak")
- 📊 **Calorie Information**: Get detailed nutritional information
- 🏷️ **Categories**: Browse foods by category
- 📱 **REST API**: Easy integration with mobile/web apps
- 🔐 **API Key Authentication**: Secure access with rate limiting
- ⚡ **Rate Limiting**: Fair usage limits (10/min, 200/hour, 500/day)
- 📚 **Auto Documentation**: Built-in Swagger UI and ReDoc
- 🚀 **Production Ready**: Deployed on Render

## Database

- **750+ Food Items** with calorie information
- **11 Food Categories** (Malaysian, International, etc.)
- **Turso Database** (libSQL) for fast, reliable data access

## API Endpoints

### Main Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `GET` | `/` | Health check | - |
| `GET` | `/foods/search?name={food}` | Search foods by name | `?name=nasi lemak` |
| `GET` | `/foods/{id}` | Get specific food by ID | `/foods/123` |
| `GET` | `/foods` | List all foods (paginated) | `?page=1&per_page=20` |
| `GET` | `/categories` | List all food categories | - |

### Quick Calorie Lookup
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/foods/search/{food_name}/calories` | Quick calorie lookup |

## Usage Examples

**Note:** All API endpoints require authentication. Get your API key first (see [Rate Limiting](#rate-limiting) section).

### Search for "Nasi Lemak"
```bash
curl "https://your-api.onrender.com/foods/search?name=nasi%20lemak" \
  -H "X-API-Key: your_api_key_here"
```

**Response:**
```json
{
  "total": 5,
  "foods": [
    {
      "id": 1,
      "name": "Nasi lemak (biasa)",
      "serving": "1 set",
      "weight_g": 250.0,
      "calories_kcal": 320.0,
      "category": "NASI, MEE, BIHUN,KUETIAU DAN LAIN- LAIN",
      "reference": "nutrition database"
    }
  ]
}
```

### Quick Calorie Lookup
```bash
curl "https://your-api.onrender.com/foods/search/rendang/calories" \
  -H "X-API-Key: your_api_key_here"
```

**Response:**
```json
{
  "food_name": "Rendang ayam",
  "calories_kcal": 100.0,
  "serving": "1 senduk",
  "total_matches": 3
}
```

## Rate Limiting

The API uses API key authentication with the following rate limits:

- **10 requests per minute**
- **200 requests per hour**
- **500 requests per day**
- **Maximum 5 concurrent requests** (across all API keys)

### Getting an API Key

For development, create a test user:
```bash
curl -X POST https://your-api.onrender.com/api/create-test-user
```

This returns an API key that you must include in all requests using the `X-API-Key` header.

### Rate Limit Headers

Every response includes rate limit information:
- `X-RateLimit-Limit-*`: Your limits
- `X-RateLimit-Remaining-*`: Requests remaining
- `Retry-After`: Seconds to wait when rate limited

See [RATE_LIMITING.md](./RATE_LIMITING.md) for detailed documentation.

## Local Development

### Prerequisites
- Python 3.8+
- Turso database account

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd kalori-makanan-kkm
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file:
```bash
TURSO_DATABASE_URL=libsql://your-database-url.turso.io
TURSO_DATABASE_TOKEN=your_database_token
```

5. **Run the API**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the API**
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment to Render

### Quick Deploy

1. **Fork/Clone this repository**

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository
   - Choose "Web Service"

3. **Configure Environment Variables**
   Add these in Render dashboard:
   ```
   TURSO_DATABASE_URL=libsql://your-database-url.turso.io
   TURSO_DATABASE_TOKEN=your_database_token
   ```

4. **Deploy Settings**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free tier works perfectly

### Alternative: render.yaml Deploy

This repository includes a `render.yaml` file for easy deployment:

1. Push to GitHub
2. Import repository in Render
3. Set environment variables
4. Deploy automatically

## API Documentation

Once deployed, your API will have automatic documentation at:
- **Swagger UI**: `https://your-app.onrender.com/docs`
- **ReDoc**: `https://your-app.onrender.com/redoc`

## Project Structure

```
kalori-makanan-kkm/
├── app/
│   ├── __init__.py         # Python package marker
│   ├── main.py             # FastAPI application
│   ├── database.py         # Database connection & queries
│   ├── models.py           # Pydantic response models
│   ├── auth.py             # Authentication & API key management
│   └── rate_limit.py       # Rate limiting middleware
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment config
├── start.sh               # Production startup script
├── example_usage.py        # Example API usage script
├── RATE_LIMITING.md       # Rate limiting documentation
└── README.md              # This file
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TURSO_DATABASE_URL` | Turso database URL | `libsql://db-name.turso.io` |
| `TURSO_DATABASE_TOKEN` | Database authentication token | `eyJhbGci...` |
| `PORT` | Server port (set by Render) | `10000` |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## License

MIT License - Feel free to use this for your projects!

## Support

- 📚 **Documentation**: Check `/docs` endpoint
- 🐛 **Issues**: Open GitHub issues
- 💬 **Questions**: Create discussions

---

**Made with ❤️ for the Malaysian food community**