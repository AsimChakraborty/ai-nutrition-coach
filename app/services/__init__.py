"""Services module for the Nutrition Coach application."""

from app.services.web_search import web_search_agent, WebSearchAgent
from app.services.logger import logger_agent, LoggerAgent
from app.services.meal_suggester import (
    meal_suggester_agent,
    MealSuggesterAgent,
)

__all__ = [
    "web_search_agent",
    "WebSearchAgent",
    "logger_agent",
    "LoggerAgent",
    "meal_suggester_agent",
    "MealSuggesterAgent",
]