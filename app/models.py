from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    """Base category model"""
    id: int
    name: str
    created_at: Optional[datetime] = None

class Category(CategoryBase):
    """Category response model"""
    class Config:
        from_attributes = True

class FoodBase(BaseModel):
    """Base food model"""
    id: int
    name: str
    serving: Optional[str] = None
    weight_g: Optional[float] = None
    calories_kcal: Optional[float] = None
    reference: Optional[str] = None
    created_at: Optional[datetime] = None

class Food(FoodBase):
    """Food response model"""
    category_id: int

    class Config:
        from_attributes = True

class FoodWithCategory(FoodBase):
    """Food response model with category information"""
    category: Optional[str] = None

    class Config:
        from_attributes = True

class FoodSearchResponse(BaseModel):
    """Response model for food search results"""
    total: int
    foods: list[FoodWithCategory]

class FoodListResponse(BaseModel):
    """Response model for paginated food list"""
    total: int
    page: int
    per_page: int
    foods: list[FoodWithCategory]

class HealthCheck(BaseModel):
    """Health check response model"""
    status: str
    message: str
    database_connected: bool
