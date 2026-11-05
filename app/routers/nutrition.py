"""Nutrition API endpoints."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query, status
from app.services import web_search_agent, logger_agent

from app.models.nutrition import (
    MealEntryResponse,
    MealSuggestion,
    MealSuggestionRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/nutrition", tags=["nutrition"])


# In-memory storage for demo (would be replaced with Google Sheets in production)
meal_log: List[MealEntryResponse] = []
meal_id_counter = 1


@router.post(
    "/log",
    response_model=MealEntryResponse,
    summary="Log a meal entry",
    description="Submit a meal to estimate calories, log it, and get a suggestion.",
)
async def log_meal(
    user_name: str = Query(..., description="Name of the user"),
    meal_description: str = Query(..., description="Description of the meal"),
) -> MealEntryResponse:
    """
    Process a meal through the complete nutrition workflow:

    1. Web Search Agent estimates calories
    2. Logger Agent records the entry
    """
    global meal_id_counter

    logger.info(f"Processing meal for {user_name}: {meal_description}")

    # Step 1: Web Search Agent - Estimate calories
    estimated_calories = await web_search_agent.estimate_calories(meal_description)
    logger.info(f"Estimated calories: {estimated_calories}")

    # Step 2: Logger Agent - Record the entry
    entry = await logger_agent.log_entry(
        user_name=user_name,
        meal_description=meal_description,
        estimated_calories=estimated_calories,
    )

    # Update with proper ID
    entry.id = meal_id_counter
    meal_id_counter += 1

    meal_log.append(entry)

    return entry


@router.get(
    "/history/{user_name}",
    response_model=List[MealEntryResponse],
    summary="Get meal history",
    description="Get all logged meals for a specific user.",
)
async def get_meal_history(user_name: str) -> List[MealEntryResponse]:
    """Get meal history for a specific user."""
    filtered_entries = [entry for entry in meal_log if entry.user_name == user_name]
    return filtered_entries


@router.get(
    "/history",
    response_model=List[MealEntryResponse],
    summary="Get all meal history",
    description="Get all logged meals.",
)
async def get_all_meal_history() -> List[MealEntryResponse]:
    """Get all meal history."""
    return meal_log


@router.post(
    "/suggest",
    response_model=MealSuggestion,
    summary="Get meal suggestion",
    description="Get a healthy follow-up meal suggestion based on the last meal.",
)
async def get_meal_suggestion(request: MealSuggestionRequest) -> MealSuggestion:
    """
    Get a healthy meal suggestion based on the user's last meal.
    """
    logger.info(f"Getting suggestion for {request.user_name}'s meal: {request.last_meal}")

    from app.services import meal_suggester_agent

    suggestion = await meal_suggester_agent.suggest_meal(request)

    return suggestion


@router.get(
    "/health",
    summary="Health check",
    description="Check if the API is running.",
)
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "Nutrition Coach API"}