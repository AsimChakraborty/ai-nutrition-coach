"""Meal suggestion service using Groq LLM API."""

import json
import logging
from typing import Optional

from groq import AsyncGroq

from config.settings import get_settings
from app.models.nutrition import MealSuggestion, MealSuggestionRequest
from app.prompts.meal_prompts import (
    DEFAULT_MEAL_PROMPT_TEMPLATE,
    MEAL_SUGGESTER_SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)


class MealSuggesterAgent:
    """Agent that suggests healthy follow-up meals using Groq LLM."""

    def __init__(self) -> None:
        """Initialize the meal suggester agent with Groq client."""
        self.settings = get_settings()
        self.client: Optional[AsyncGroq] = None

        if self.settings.groq_api_key:
            self.client = AsyncGroq(api_key=self.settings.groq_api_key)

    async def suggest_meal(self, request: MealSuggestionRequest) -> MealSuggestion:
        """
        Suggest a healthy follow-up meal based on the last meal.

        Args:
            request: MealSuggestionRequest with user info and last meal

        Returns:
            MealSuggestion with meal details and recipe
        """
        logger.info(f"Generating meal suggestion for: {request.user_name}")

        # Check if Groq is configured
        if not self.client:
            logger.warning("Groq not configured, using fallback suggestion")
            return self._get_fallback_suggestion(request)

        try:
            return await self._generate_suggestion_with_groq(request)
        except Exception as e:
            logger.error(f"Error generating suggestion with Groq: {e}")
            return self._get_fallback_suggestion(request)

    async def _generate_suggestion_with_groq(
        self, request: MealSuggestionRequest
    ) -> MealSuggestion:
        """Generate meal suggestion using Groq API."""
        prompt = self._build_prompt(request)

        response = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": MEAL_SUGGESTER_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        response_text = response.choices[0].message.content
        logger.info(f"Groq response: {response_text}")

        # Parse the JSON response
        data = json.loads(response_text)

        return MealSuggestion(
            estimated_calories_per_serving=data.get("estimated_calories_per_serving", 400),
            nutritional_benefits=data.get("nutritional_benefits", ""),
            why_this_meal=data.get("why_this_meal", "Balanced nutrition choice"),
            recipe=data.get("recipe", ""),
            target_daily_calories=data.get("target_daily_calories", 2000),
            # Legacy fields (keeping for backwards compatibility)
            meal_name=data.get("meal_name", "Healthy Meal"),
            description=data.get("description", ""),
            estimated_calories=data.get("estimated_calories", data.get("estimated_calories_per_serving", 400)),
            reasoning=data.get("reasoning", data.get("why_this_meal", "")),
        )

    def _build_prompt(self, request: MealSuggestionRequest) -> str:
        """Build the prompt for the LLM."""
        return DEFAULT_MEAL_PROMPT_TEMPLATE.format(
            last_meal=request.last_meal,
            target_daily_calories=request.target_daily_calories,
        )

    def _get_fallback_suggestion(
        self, request: MealSuggestionRequest
    ) -> MealSuggestion:
        """Provide a fallback suggestion when Groq is not available."""
        estimated_calories = self._estimate_calories_fallback(request.last_meal)
        return MealSuggestion(
            meal_name="Grilled Salmon with Quinoa and Vegetables",
            description="A protein-rich meal with omega-3 fatty acids, complex carbs, and fresh vegetables.",
            recipe="""1. Season salmon fillet with lemon, dill, salt, and pepper.
                        2. Grill for 4-5 minutes per side.
                        3. Cook quinoa according to package instructions.
                        4. Steam broccoli and asparagus.
                        5. Serve salmon on quinoa with vegetables on the side.""",
            estimated_calories=estimated_calories,
            reasoning="This meal provides protein for muscle recovery, omega-3 for brain health, and complex carbs for sustained energy.",
        )

    def _estimate_calories_fallback(self, last_meal: str) -> int:
        """Estimate calories from meal description using simple heuristic."""
        import re

        meal_lower = last_meal.lower().strip()

        # Known meal estimates (same database as web_search.py _parse_common_meals)
        meal_estimates = {
            "chicken salad": 350,
            "chicken salad with olive oil": 450,
            "chicken salad with olive oil dressing": 500,
            "grilled chicken salad": 400,
            "caesar salad": 350,
            "caesar salad with chicken": 500,
            "greek salad": 250,
            "vegetable salad": 150,
            "tuna salad": 300,
            "salad": 200,
            "grilled chicken": 300,
            "fried chicken": 400,
            "roasted chicken": 350,
            "chicken breast": 250,
            "chicken curry": 350,
            "chicken roast": 400,
            "beef steak": 450,
            "beef curry": 400,
            "mutton curry": 450,
            "grilled fish": 200,
            "fried fish": 300,
            "pasta": 400,
            "spaghetti": 450,
            "pasta with chicken": 550,
            "mac and cheese": 500,
            "pizza": 285,
            "burger": 550,
            "cheeseburger": 650,
            "sandwich": 400,
            "chicken sandwich": 450,
            "hot dog": 300,
            "french fries": 365,
            "nuggets": 300,
            "taco": 170,
            "tacos": 300,
            "burrito": 500,
            "quesadilla": 450,
            "nachos": 400,
            "sushi": 350,
            "ramen": 450,
            "fried rice": 450,
            "chicken fried rice": 550,
            "stir fry": 400,
            "noodles": 400,
            "chicken noodles": 450,
            "rice bowl": 500,
            "dumplings": 300,
            "polao": 350,
            "plain rice": 200,
            "white rice": 200,
            "rice": 200,
            "dal": 150,
            "rice and dal": 350,
            "chicken biryani": 650,
            "beef biryani": 750,
            "khichuri": 400,
            "paratha": 300,
            "roti": 120,
            "chapati": 120,
            "naan": 300,
            "chicken korma": 450,
            "chicken curry with rice": 550,
            "beef curry with rice": 600,
            "vegetable curry": 200,
            "singara": 180,
            "samosa": 200,
            "fuchka": 250,
            "chotpoti": 300,
            "chicken roast with rice": 550,
            "boiled egg": 78,
            "fried egg": 120,
            "omelette": 180,
            "scrambled eggs": 180,
            "oatmeal": 150,
            "pancakes": 350,
            "toast": 80,
            "peanut butter toast": 200,
            "cereal with milk": 250,
            "apple": 95,
            "banana": 105,
            "orange": 62,
            "mango": 100,
            "grapes": 100,
            "watermelon": 85,
            "papaya": 60,
            "pineapple": 80,
            "almonds": 165,
            "peanuts": 160,
            "yogurt": 150,
            "greek yogurt": 130,
            "protein bar": 200,
            "dark chocolate": 170,
            "popcorn": 100,
            "soup": 250,
            "chicken soup": 180,
            "vegetable soup": 120,
            "tomato soup": 150,
            "water": 0,
            "black coffee": 2,
            "coffee": 2,
            "milk": 150,
            "orange juice": 110,
            "soft drink": 140,
            "green tea": 2,
            "tea": 2,
            "milk tea": 120,
            "lassi": 200,
        }

        # Check exact match first
        if meal_lower in meal_estimates:
            return meal_estimates[meal_lower]

        # Check for quantity patterns (e.g., "2 eggs", "3 cups rice")
        # Pattern: capturing number followed by unit of measurement (includes plurals)
        quantity_pattern = r'(?:^|\s)(\d+)\s*(?:cup|cups|piece|pieces|slice|slices|g|gram|grams|kg|oz|ounce|tbsp|tsp|tablespoon|teaspoon|small|medium|large|egg|eggs)(?:s|\b)'
        quantity_match = re.search(quantity_pattern, meal_lower)

        if quantity_match:
            number = int(quantity_match.group(1))
            # Get the unit from the matched text
            matched_text = quantity_match.group(0)
            # Remove the number to get the unit part
            # Handle both "100 g" and "100g" formats
            after_number = matched_text[len(str(number)):].strip()
            unit_part = after_number if after_number else ''

            # Map units to approximate calories per unit
            unit_calories = {
                "egg": 78,
                "eggs": 78,
                "cup": 206,
                "cups": 206,
                "slice": 78,
                "slices": 78,
                "piece": 78,
                "pieces": 78,
                "g": 1,
                "gram": 1,
                "grams": 1,
                "kg": 1000,
                "oz": 28,
                "ounce": 28,
                "ounces": 28,
                "tbsp": 120,
                "tablespoon": 120,
                "tsp": 40,
                "teaspoon": 40,
                "small": 100,
                "medium": 200,
                "large": 300,
            }

            per_unit = unit_calories.get(unit_part, 100)
            return number * per_unit

        # Default fallback if nothing matches
        return 400


# Service instance for dependency injection
meal_suggester_agent = MealSuggesterAgent()