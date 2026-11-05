"""Data models for the Nutrition Coach application."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MealEntry(BaseModel):
    """Model for a logged meal entry."""

    user_name: str = Field(..., description="Name of the user")
    meal_description: str = Field(..., description="Description of the meal")
    estimated_calories: Optional[int] = Field(None, description="Estimated calorie count")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Entry timestamp")


class MealEntryResponse(BaseModel):
    """Response model for a logged meal entry."""

    id: int = Field(..., description="Row ID in the log")
    user_name: str = Field(..., description="Name of the user")
    meal_description: str = Field(..., description="Description of the meal")
    estimated_calories: Optional[int] = Field(None, description="Estimated calorie count")
    timestamp: str = Field(..., description="Entry timestamp in ISO format")


class MealSuggestionRequest(BaseModel):
    """Request model for meal suggestion."""

    user_name: str = Field(..., description="Name of the user")
    last_meal: str = Field(..., description="Description of the last meal eaten")
    target_daily_calories: Optional[int] = Field(
        default=2000,
        description="Target daily calorie intake",
    )


class MealSuggestion(BaseModel):
    """Model for a suggested meal."""

    meal_name: Optional[str] = Field(None, description="Name of the suggested meal (optional)")
    estimated_calories_per_serving: int = Field(..., description="Estimated calories per serving")
    nutritional_benefits: str = Field(..., description="Nutritional benefits including protein, fats, carbs, fiber")
    why_this_meal: str = Field(..., description="Why this meal is recommended")
    recipe: str = Field(..., description="Recipe instructions")
    target_daily_calories: int = Field(..., description="Target daily calorie intake for context")
    
    # Legacy fields for backwards compatibility
    description: Optional[str] = Field(None, description="Legacy: description of the meal")
    estimated_calories: Optional[int] = Field(None, description="Legacy: estimated calories")
    reasoning: Optional[str] = Field(None, description="Legacy: reasoning for suggestion")