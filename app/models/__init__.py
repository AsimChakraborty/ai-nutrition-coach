"""Data models for the Nutrition Coach application."""

from app.models.nutrition import (
    MealEntry,
    MealEntryResponse,
    MealSuggestion,
    MealSuggestionRequest,
)

__all__ = [
    "MealEntry",
    "MealEntryResponse",
    "MealSuggestion",
    "MealSuggestionRequest",
]