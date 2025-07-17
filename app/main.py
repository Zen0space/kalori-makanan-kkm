from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

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

# Create FastAPI app
app = FastAPI(
    title="Kalori Makanan API",
    description="Food calorie lookup API for Malaysian and international foods",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    line-height: 1.6;
                    color: #1a202c;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                    min-height: 100vh;
                    position: relative;
                    overflow-x: hidden;
                }}

                body::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-image:
                        radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 40% 80%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
                    animation: float 20s ease-in-out infinite;
                }}

                @keyframes float {{
                    0%, 100% {{ transform: translateY(0px); }}
                    50% {{ transform: translateY(-20px); }}
                }}

                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                    position: relative;
                    z-index: 1;
                }}

                .header {{
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 24px;
                    padding: 3rem;
                    margin-bottom: 2rem;
                    text-align: center;
                    box-shadow:
                        0 8px 32px rgba(0, 0, 0, 0.1),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2);
                    transition: all 0.3s ease;
                }}

                .header:hover {{
                    transform: translateY(-5px);
                    box-shadow:
                        0 20px 40px rgba(0, 0, 0, 0.15),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2);
                }}

                .header h1 {{
                    font-size: clamp(2.5rem, 5vw, 4rem);
                    font-weight: 800;
                    background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 1rem;
                    letter-spacing: -0.02em;
                }}

                .header p {{
                    font-size: 1.25rem;
                    color: #4a5568;
                    margin-bottom: 2rem;
                    font-weight: 400;
                    max-width: 600px;
                    margin-left: auto;
                    margin-right: auto;
                    line-height: 1.7;
                }}

                .status {{
                    display: inline-flex;
                    align-items: center;
                    background: rgba(34, 197, 94, 0.9);
                    color: white;
                    padding: 0.75rem 1.5rem;
                    border-radius: 50px;
                    font-weight: 600;
                    font-size: 0.9rem;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
                    animation: pulse 2s infinite;
                }}

                @keyframes pulse {{
                    0%, 100% {{ box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3); }}
                    50% {{ box-shadow: 0 4px 25px rgba(34, 197, 94, 0.5); }}
                }}

                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1.5rem;
                    margin: 3rem 0;
                }}

                .stat-card {{
                    background: rgba(255, 255, 255, 0.08);
                    backdrop-filter: blur(15px);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    padding: 2rem 1.5rem;
                    border-radius: 20px;
                    text-align: center;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }}

                .stat-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: linear-gradient(90deg, #667eea, #764ba2);
                    border-radius: 20px 20px 0 0;
                }}

                .stat-card:hover {{
                    transform: translateY(-8px);
                    background: rgba(255, 255, 255, 0.12);
                    border-color: rgba(255, 255, 255, 0.25);
                }}

                .stat-number {{
                    font-size: 2.5rem;
                    font-weight: 800;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 0.5rem;
                }}

                .stat-card div:last-child {{
                    color: #4a5568;
                    font-weight: 500;
                    font-size: 1rem;
                }}

                .section {{
                    background: rgba(255, 255, 255, 0.08);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 24px;
                    padding: 2.5rem;
                    margin-bottom: 1.5rem;
                    transition: all 0.3s ease;
                }}

                .section:hover {{
                    background: rgba(255, 255, 255, 0.12);
                    border-color: rgba(255, 255, 255, 0.25);
                }}

                .section h2 {{
                    color: #1a202c;
                    margin-bottom: 1.5rem;
                    font-size: 2rem;
                    font-weight: 700;
                    letter-spacing: -0.01em;
                }}

                .example-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                    gap: 1.5rem;
                }}

                .example-card {{
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    padding: 1.5rem;
                    border-radius: 16px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    transition: all 0.3s ease;
                }}

                .example-card:hover {{
                    background: rgba(255, 255, 255, 0.08);
                    transform: translateY(-3px);
                }}

                .example-card h3 {{
                    color: #2d3748;
                    margin-bottom: 1rem;
                    font-weight: 600;
                    font-size: 1.1rem;
                }}

                .api-link {{
                    color: #667eea;
                    text-decoration: none;
                    font-family: 'JetBrains Mono', 'Fira Code', monospace;
                    background: rgba(102, 126, 234, 0.1);
                    padding: 0.75rem 1rem;
                    border-radius: 12px;
                    display: inline-block;
                    margin: 0.5rem 0;
                    transition: all 0.3s ease;
                    border: 1px solid rgba(102, 126, 234, 0.2);
                    font-size: 0.9rem;
                }}

                .api-link:hover {{
                    background: rgba(102, 126, 234, 0.9);
                    color: white;
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
                }}

                .btn {{
                    display: inline-flex;
                    align-items: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 1rem 2rem;
                    border-radius: 50px;
                    text-decoration: none;
                    font-weight: 600;
                    margin: 0.75rem 0.5rem;
                    transition: all 0.3s ease;
                    border: none;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                    position: relative;
                    overflow: hidden;
                }}

                .btn::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                    transition: left 0.5s;
                }}

                .btn:hover::before {{
                    left: 100%;
                }}

                .btn:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
                }}

                .btn-secondary {{
                    background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                    box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
                }}

                .btn-secondary:hover {{
                    box-shadow: 0 8px 25px rgba(72, 187, 120, 0.4);
                }}

                .code {{
                    background: rgba(45, 55, 72, 0.9);
                    backdrop-filter: blur(10px);
                    color: #e2e8f0;
                    padding: 1.5rem;
                    border-radius: 16px;
                    font-family: 'JetBrains Mono', 'Fira Code', monospace;
                    font-size: 0.9rem;
                    overflow-x: auto;
                    margin: 1rem 0;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}

                .highlight {{
                    background: rgba(246, 173, 85, 0.1);
                    border-left: 4px solid #f6ad55;
                    padding: 1.5rem;
                    border-radius: 0 16px 16px 0;
                    margin: 1rem 0;
                    backdrop-filter: blur(10px);
                    border-top: 1px solid rgba(246, 173, 85, 0.2);
                    border-right: 1px solid rgba(246, 173, 85, 0.2);
                    border-bottom: 1px solid rgba(246, 173, 85, 0.2);
                }}

                .footer {{
                    text-align: center;
                    padding: 2rem;
                    color: rgba(255, 255, 255, 0.8);
                    font-weight: 400;
                }}

                @media (max-width: 768px) {{
                    .container {{ padding: 1rem; }}
                    .header {{ padding: 2rem 1.5rem; }}
                    .header h1 {{ font-size: 2.5rem; }}
                    .stats {{ grid-template-columns: 1fr; gap: 1rem; }}
                    .example-grid {{ grid-template-columns: 1fr; }}
                    .btn {{ margin: 0.5rem 0; width: 100%; justify-content: center; }}
                }}

                @media (max-width: 480px) {{
                    .header {{ padding: 1.5rem 1rem; }}
                    .section {{ padding: 1.5rem; }}
                    .stat-card {{ padding: 1.5rem 1rem; }}
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
