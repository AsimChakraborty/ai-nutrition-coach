"""Nutrition Coach application package."""

from app.main import app
from app.models import MealEntry, MealSuggestion
from app.routers import nutrition_router
from app.services import logger_agent, meal_suggester_agent, web_search_agent

__version__ = "1.0.0"

__all__ = [
    "app",
    "MealEntry",
    "MealSuggestion",
    "nutrition_router",
    "logger_agent",
    "meal_suggester_agent",
    "web_search_agent",
]