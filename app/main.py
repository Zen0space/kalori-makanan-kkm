from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
import uvicorn
import os
from pathlib import Path
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

# Create FastAPI app
app = FastAPI(
    title="Kalori Makanan API",
    description="Food calorie lookup API for Malaysian and international foods",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files for React app
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Serve React app if available, otherwise fallback to HTML landing page"""
    # Check if React build exists
    static_dir = Path(__file__).parent / "static"
    index_file = static_dir / "index.html"

    if index_file.exists():
        return FileResponse(index_file)

    # Fallback to original HTML landing page
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
                    color: #333;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: white;
                    border-radius: 16px;
                    padding: 40px;
                    margin-bottom: 30px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .header h1 {{
                    font-size: 3rem;
                    color: #2d3748;
                    margin-bottom: 10px;
                }}
                .header p {{
                    font-size: 1.2rem;
                    color: #666;
                    margin-bottom: 20px;
                }}
                .status {{
                    display: inline-block;
                    background: {status_color};
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
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
                    background: #f8fafc;
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    border-left: 4px solid #667eea;
                }}
                .stat-number {{
                    font-size: 2rem;
                    font-weight: bold;
                    color: #667eea;
                }}
                .section {{
                    background: white;
                    border-radius: 16px;
                    padding: 30px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.07);
                }}
                .section h2 {{
                    color: #2d3748;
                    margin-bottom: 20px;
                    font-size: 1.8rem;
                }}
                .example-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                }}
                .example-card {{
                    background: #f8fafc;
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                }}
                .example-card h3 {{
                    color: #4a5568;
                    margin-bottom: 10px;
                }}
                .api-link {{
                    color: #667eea;
                    text-decoration: none;
                    font-family: monospace;
                    background: #edf2f7;
                    padding: 8px 12px;
                    border-radius: 6px;
                    display: inline-block;
                    margin: 5px 0;
                    transition: all 0.2s;
                }}
                .api-link:hover {{
                    background: #667eea;
                    color: white;
                    transform: translateY(-1px);
                }}
                .btn {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 24px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 600;
                    margin: 10px 10px 10px 0;
                    transition: all 0.2s;
                }}
                .btn:hover {{
                    background: #5a67d8;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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
                    padding: 15px;
                    border-radius: 8px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9rem;
                    overflow-x: auto;
                    margin: 10px 0;
                }}
                .highlight {{
                    background: #fef5e7;
                    border-left: 4px solid #f6ad55;
                    padding: 15px;
                    border-radius: 0 8px 8px 0;
                    margin: 15px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: white;
                    opacity: 0.8;
                }}
                @media (max-width: 768px) {{
                    .container {{ padding: 10px; }}
                    .header {{ padding: 20px; }}
                    .header h1 {{ font-size: 2rem; }}
                    .stats {{ grid-template-columns: 1fr; }}
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
    name: str = Query(..., description="Food name to search for", example="nasi lemak")
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
async def get_food_detail(food_id: int):
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
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page (max 100)")
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
async def list_categories():
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
async def get_food_calories(food_name: str):
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

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
