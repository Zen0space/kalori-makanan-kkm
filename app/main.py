from fastapi import FastAPI, HTTPException, Query, Depends, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from typing import Optional, List
import uvicorn
import os

from .database import (
    test_connection,
    get_food_by_name,
    get_food_by_id,
    get_all_foods,
    get_total_foods,
    get_all_categories
)
from .models import (
    HealthCheck,
    FoodWithCategory,
    FoodSearchResponse,
    FoodListResponse,
    Category
)
from .auth import (
    create_api_key_for_user,
    create_test_user_and_key,
    cleanup_old_logs
)
from .rate_limit import (
    require_api_key,
    get_rate_limit_status
)

# Models for API key management
class CreateUserRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class CreateApiKeyRequest(BaseModel):
    user_id: int
    name: Optional[str] = None

# Create FastAPI app
app = FastAPI(
    title="Kalori Makanan API",
    description="Food calorie lookup API for Malaysian and international foods",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Beautiful HTML landing page for the API"""
    try:
        # Get database statistics
        db_connected = test_connection()
        total_foods = get_total_foods() if db_connected else 0
        categories = get_all_categories() if db_connected else []

        # Sample food for demo
        sample_food = None
        if db_connected:
            try:
                sample_foods = get_food_by_name("nasi lemak")
                sample_food = sample_foods[0] if sample_foods else None
            except:
                pass

        status_color = "#22c55e" if db_connected else "#ef4444"
        status_text = "🟢 Online" if db_connected else "🔴 Offline"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Kalori Makanan API 🍽️</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #2d3748;
                    background: #f7fafc;
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                    text-align: center;
                    border: 1px solid #e2e8f0;
                }}
                .header h1 {{
                    font-size: 2.5rem;
                    color: #1a202c;
                    margin-bottom: 12px;
                    font-weight: 700;
                }}
                .header p {{
                    font-size: 1.1rem;
                    color: #718096;
                    margin-bottom: 24px;
                }}
                .status {{
                    display: inline-block;
                    background: {status_color};
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 0.9rem;
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                .stat-card {{
                    background: #f7fafc;
                    padding: 24px;
                    border-radius: 8px;
                    text-align: center;
                    border: 1px solid #e2e8f0;
                    transition: transform 0.2s ease;
                }}
                .stat-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                .stat-number {{
                    font-size: 2rem;
                    font-weight: 700;
                    color: #4299e1;
                    margin-bottom: 4px;
                }}
                .section {{
                    background: white;
                    border-radius: 12px;
                    padding: 32px;
                    margin-bottom: 24px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                    border: 1px solid #e2e8f0;
                }}
                .section h2 {{
                    color: #1a202c;
                    margin-bottom: 20px;
                    font-size: 1.5rem;
                    font-weight: 600;
                }}
                .example-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                }}
                .example-card {{
                    background: #f7fafc;
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                }}
                .example-card h3 {{
                    color: #2d3748;
                    margin-bottom: 12px;
                    font-weight: 600;
                }}
                .api-link {{
                    color: #4299e1;
                    text-decoration: none;
                    font-family: 'Monaco', 'Menlo', monospace;
                    background: #edf2f7;
                    padding: 8px 12px;
                    border-radius: 4px;
                    display: inline-block;
                    margin: 4px 0;
                    font-size: 0.9rem;
                    transition: all 0.2s ease;
                }}
                .api-link:hover {{
                    background: #4299e1;
                    color: white;
                }}
                .btn {{
                    display: inline-block;
                    background: #4299e1;
                    color: white;
                    padding: 12px 24px;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: 600;
                    margin: 8px 8px 8px 0;
                    transition: all 0.2s ease;
                }}
                .btn:hover {{
                    background: #3182ce;
                    transform: translateY(-1px);
                }}
                .btn-secondary {{
                    background: #48bb78;
                }}
                .btn-secondary:hover {{
                    background: #38a169;
                }}
                .code {{
                    background: #2d3748;
                    color: #e2e8f0;
                    padding: 16px;
                    border-radius: 6px;
                    font-family: 'Monaco', 'Menlo', monospace;
                    font-size: 0.9rem;
                    overflow-x: auto;
                    margin: 12px 0;
                }}
                .highlight {{
                    background: #fef5e7;
                    border-left: 4px solid #f6ad55;
                    padding: 16px;
                    border-radius: 0 6px 6px 0;
                    margin: 16px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 24px;
                    color: #718096;
                }}
                @media (max-width: 768px) {{
                    .container {{ padding: 16px; }}
                    .header {{ padding: 24px; }}
                    .header h1 {{ font-size: 2rem; }}
                    .stats {{ grid-template-columns: 1fr; }}
                    .example-grid {{ grid-template-columns: 1fr; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🍽️ Kalori Makanan API</h1>
                    <p>Fast & reliable food calorie lookup for Malaysian and international cuisine</p>
                    <span class="status">{status_text}</span>

                    <div class="stats">
                        <div class="stat-card">
                            <div class="stat-number">{total_foods}+</div>
                            <div>Food Items</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{len(categories)}</div>
                            <div>Categories</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">REST</div>
                            <div>API Standard</div>
                        </div>
                    </div>

                    <div>
                        <a href="/docs" class="btn">📚 API Documentation</a>
                        <a href="/redoc" class="btn btn-secondary">📖 ReDoc</a>
                    </div>
                </div>

                <div class="section">
                    <h2>🚀 Quick Start</h2>
                    <p>Try these examples right now by clicking the links below:</p>

                    <div class="example-grid">
                        <div class="example-card">
                            <h3>🔍 Search Foods</h3>
                            <p>Find calorie information by food name</p>
                            <a href="/foods/search?name=nasi%20lemak" class="api-link" target="_blank">
                                /foods/search?name=nasi lemak
                            </a>
                            <a href="/foods/search?name=rendang" class="api-link" target="_blank">
                                /foods/search?name=rendang
                            </a>
                            <a href="/foods/search?name=ayam" class="api-link" target="_blank">
                                /foods/search?name=ayam
                            </a>
                        </div>

                        <div class="example-card">
                            <h3>📊 Browse Categories</h3>
                            <p>Explore food categories available</p>
                            <a href="/categories" class="api-link" target="_blank">
                                /categories
                            </a>
                        </div>

                        <div class="example-card">
                            <h3>📋 List Foods</h3>
                            <p>Browse paginated food database</p>
                            <a href="/foods?page=1&per_page=10" class="api-link" target="_blank">
                                /foods?page=1&per_page=10
                            </a>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>💡 Example Response</h2>
                    <p>Here's what you get when searching for food calories:</p>

                    <div class="code">
GET /foods/search?name=nasi%20lemak

{{
  "total": 5,
  "foods": [
    {{
      "id": 1,
      "name": "Nasi lemak (biasa)",
      "serving": "1 set",
      "weight_g": 250.0,
      "calories_kcal": 320.0,
      "category": "NASI, MEE, BIHUN,KUETIAU DAN LAIN- LAIN",
      "reference": "nutrition database"
    }}
  ]
}}
                    </div>
                </div>

                <div class="section">
                    <h2>🛠️ Integration</h2>
                    <p>Easy to integrate with any application:</p>

                    <div class="example-grid">
                        <div class="example-card">
                            <h3>cURL</h3>
                            <div class="code">curl "https://kalori-makanan-kkm.onrender.com/foods/search?name=nasi%20lemak"</div>
                        </div>

                        <div class="example-card">
                            <h3>JavaScript</h3>
                            <div class="code">fetch('/foods/search?name=nasi%20lemak')
  .then(res => res.json())
  .then(data => console.log(data))</div>
                        </div>

                        <div class="example-card">
                            <h3>Python</h3>
                            <div class="code">import requests
r = requests.get('/foods/search?name=nasi%20lemak')
data = r.json()</div>
                        </div>
                    </div>
                </div>

                <div class="highlight">
                    <strong>🎯 Perfect for:</strong> Nutrition apps, calorie trackers, meal planners, health applications, food databases, and Malaysian cuisine applications.
                </div>
            </div>

            <div class="footer">
                <p>Made with ❤️ for the Malaysian food community | Powered by FastAPI & Turso</p>
            </div>
        </body>
        </html>
        """

        return html_content

    except Exception as e:
        # Fallback simple HTML if there's an error
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Kalori Makanan API</title></head>
        <body>
            <h1>🍽️ Kalori Makanan API</h1>
            <p>Food calorie lookup API</p>
            <p><a href="/docs">API Documentation</a></p>
            <p>Error loading full page: {str(e)}</p>
        </body>
        </html>
        """

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint to verify API and database connectivity"""
    try:
        db_connected = test_connection()
        if db_connected:
            return HealthCheck(
                status="healthy",
                message="API is running and database is connected",
                database_connected=True
            )
        else:
            return HealthCheck(
                status="unhealthy",
                message="API is running but database connection failed",
                database_connected=False
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@app.get("/foods/search", response_model=FoodSearchResponse)
async def search_foods(
    request: Request,
    response: Response,
    name: str = Query(..., description="Food name to search for", example="nasi lemak"),
    auth=Depends(require_api_key)
):
    """Search for foods by name - Main feature for calorie lookup"""
    try:
        if not name or len(name.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Search term must be at least 2 characters long"
            )

        results = get_food_by_name(name.strip())

        foods = []
        for row in results:
            # row format: id, name, serving, weight_g, calories_kcal, reference, category
            food = FoodWithCategory(
                id=row[0],
                name=row[1],
                serving=row[2],
                weight_g=row[3],
                calories_kcal=row[4],
                reference=row[5],
                category=row[6]
            )
            foods.append(food)

        return FoodSearchResponse(
            total=len(foods),
            foods=foods
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching for foods: {str(e)}"
        )

@app.get("/foods/{food_id}", response_model=FoodWithCategory)
async def get_food_detail(
    food_id: int,
    request: Request,
    response: Response,
    auth=Depends(require_api_key)
):
    """Get detailed information about a specific food by its ID"""
    try:
        result = get_food_by_id(food_id)

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Food with ID {food_id} not found"
            )

        # result format: id, name, serving, weight_g, calories_kcal, reference, category
        food = FoodWithCategory(
            id=result[0],
            name=result[1],
            serving=result[2],
            weight_g=result[3],
            calories_kcal=result[4],
            reference=result[5],
            category=result[6]
        )

        return food

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving food details: {str(e)}"
        )

@app.get("/foods", response_model=FoodListResponse)
async def list_foods(
    request: Request,
    response: Response,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    auth=Depends(require_api_key)
):
    """Get paginated list of all foods"""
    try:
        # Calculate offset
        offset = (page - 1) * per_page

        # Get total count and foods
        total_foods = get_total_foods()
        results = get_all_foods(limit=per_page, offset=offset)

        foods = []
        for row in results:
            # row format: id, name, serving, weight_g, calories_kcal, reference, category
            food = FoodWithCategory(
                id=row[0],
                name=row[1],
                serving=row[2],
                weight_g=row[3],
                calories_kcal=row[4],
                reference=row[5],
                category=row[6]
            )
            foods.append(food)

        return FoodListResponse(
            total=total_foods,
            page=page,
            per_page=per_page,
            foods=foods
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving foods list: {str(e)}"
        )

@app.get("/categories", response_model=List[Category])
async def list_categories(
    request: Request,
    response: Response,
    auth=Depends(require_api_key)
):
    """Get list of all food categories"""
    try:
        results = get_all_categories()

        categories = []
        for row in results:
            # row format: id, name
            category = Category(
                id=row[0],
                name=row[1]
            )
            categories.append(category)

        return categories

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving categories: {str(e)}"
        )

# Additional endpoint for quick calorie lookup
@app.get("/foods/search/{food_name}/calories")
async def get_food_calories(
    food_name: str,
    request: Request,
    response: Response,
    auth=Depends(require_api_key)
):
    """Quick endpoint to get just the calories for a specific food"""
    try:
        results = get_food_by_name(food_name)

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No food found matching '{food_name}'"
            )

        # Return the first match with basic info
        first_result = results[0]
        return {
            "food_name": first_result[1],
            "calories_kcal": first_result[4],
            "serving": first_result[2],
            "total_matches": len(results)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting food calories: {str(e)}"
        )

# API Key Management Endpoints (these don't require API key)
@app.post("/api/create-test-user", tags=["Authentication"])
async def create_test_user():
    """
    Create a test user and API key for development.
    This endpoint is only for testing and should be removed in production.
    """
    try:
        result = create_test_user_and_key()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create-api-key", tags=["Authentication"])
async def create_api_key(request: CreateApiKeyRequest):
    """
    Create a new API key for a user.
    In production, this should be protected by proper authentication.
    """
    try:
        result = create_api_key_for_user(request.user_id, request.name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rate-limit-status", tags=["Authentication"])
async def check_rate_limit_status(
    request: Request,
    response: Response,
    auth=Depends(require_api_key)
):
    """
    Check current rate limit status for your API key.
    """
    try:
        # Get API key from header
        api_key = request.headers.get("x-api-key")
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")

        status = await get_rate_limit_status(api_key)

        # Add rate limit headers to response
        if hasattr(request.state, 'rate_limit_headers'):
            for header, value in request.state.rate_limit_headers.items():
                response.headers[header] = value

        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cleanup-logs", tags=["Maintenance"])
async def cleanup_logs(days_to_keep: int = 7):
    """
    Clean up old rate limit logs.
    This should be run periodically to prevent database bloat.
    In production, this should be a scheduled job, not an API endpoint.
    """
    try:
        deleted_count = cleanup_old_logs(days_to_keep)
        return {
            "message": f"Cleaned up {deleted_count} old log entries",
            "days_kept": days_to_keep
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Startup event to ensure database is ready
@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    # Test database connection
    if not test_connection():
        print("WARNING: Database connection failed at startup")
    else:
        print("Database connection successful")

        # Optional: Create a test user on first run
        # Uncomment the following lines for development
        # try:
        #     result = create_test_user_and_key()
        #     print(f"Test user created. API Key: {result['api_key']}")
        # except Exception as e:
        #     print(f"Test user creation skipped: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
