from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
import uvicorn
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

@app.get("/", response_model=HealthCheck)
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
