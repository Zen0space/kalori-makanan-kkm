# FastAPI Food Calorie Lookup API - Todo

## Project Overview
Simple FastAPI application to lookup food calories from Turso database. Example: search "nasi lemak" → get calorie information.

## Database Schema (Already exists)
- **foods**: id, category_id, name, serving, weight_g, calories_kcal, reference, created_at
- **categories**: id, name, created_at

## Project Structure
```
kalori-makanan-kkm/
├── app/
│   ├── __init__.py         # Empty file to make it a Python package
│   ├── main.py             # FastAPI application entry point
│   ├── database.py         # Turso database connection
│   └── models.py           # Pydantic models for API responses
├── .env                    # Environment variables (Turso URL & Token)
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment config
└── todo.md                 # This file
```

## Todo Tasks

### 1. Project Setup
- [x] Create `requirements.txt` with dependencies:
  - fastapi
  - uvicorn
  - libsql
  - python-dotenv
- [x] Create `.env` file (use env.examples.txt as reference)
- [x] Create basic project structure

### 2. Database Connection
- [x] Create `database.py` - Turso connection setup
- [x] Create `models.py` - Pydantic models for Food and Category
- [x] Test database connection

### 3. API Endpoints
- [x] Create `main.py` with FastAPI app
- [x] **GET /** - Health check endpoint
- [x] **GET /foods/search?name={food_name}** - Search foods by name (main feature)
- [x] **GET /foods/{id}** - Get specific food by ID
- [x] **GET /foods** - List all foods (with pagination)
- [x] **GET /categories** - List all categories
- [x] Test all endpoints locally

### 4. Render Deployment
- [x] Create `render.yaml` deployment config
- [x] Create production startup script and README
- [x] Test deployment on Render
- [x] Verify API works on Render URL
- [x] Create beautiful landing page for homepage

## Suggested API Response Format
```json
{
  "id": 1,
  "name": "nasi lemak",
  "serving": "1 plate",
  "weight_g": 250.0,
  "calories_kcal": 644.0,
  "category": "Malaysian Food",
  "reference": "nutrition database"
}
```

## Development Notes
- Keep it simple - no authentication needed yet
- Use Zed editor with Claude assistance
- Deploy to Render (no custom domain needed)
- Focus on food search functionality first

```

To test the setup:
```bash
source venv/bin/activate
python test_db.py
```
