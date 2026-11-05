"""Web search service for calorie estimation using LLM and local database."""

import json
import logging
import re
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
from groq import AsyncGroq

from config.settings import get_settings

logger = logging.getLogger(__name__)


class WebSearchAgent:
    """Agent that searches for nutritional information and uses LLM for calorie estimation."""

    def __init__(self) -> None:
        """Initialize the web search agent."""
        self.settings = get_settings()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        
        # Initialize Groq client if API key is available
        self.llm_client: Optional[AsyncGroq] = None
        if self.settings.groq_api_key:
            self.llm_client = AsyncGroq(api_key=self.settings.groq_api_key)

    async def estimate_calories(self, meal_description: str) -> Optional[int]:
        """
        Estimate calories for a given meal description.
        
        Tries multiple methods:
        1. Local food database
        2. Web search
        3. LLM fallback (if available)

        Args:
            meal_description: Description of the meal (e.g., "2 eggs, 3 cup rice")

        Returns:
            Estimated calorie count or None if not found
        """
        logger.info(f"Estimating calories for: {meal_description}")

        # First, try local food database
        local_calories = self._parse_common_meals(meal_description)
        if local_calories:
            logger.info(f"Found in local database: {local_calories} calories")
            return local_calories

        # Second, try web search
        web_calories = await self._search_nutritionix(meal_description)
        if web_calories:
            logger.info(f"Found via web search: {web_calories} calories")
            return web_calories

        # Third, try LLM if available (for unknown foods like "2 eggs, 3 cup rice")
        if self.llm_client:
            llm_calories = await self._estimate_with_llm(meal_description)
            if llm_calories:
                logger.info(f"Found via LLM: {llm_calories} calories")
                return llm_calories

        logger.warning(f"Could not find calorie info for: {meal_description}")
        return None

    async def _estimate_with_llm(self, meal_description: str) -> Optional[int]:
        """
        Use LLM to estimate calories when other methods fail.
        Parses quantities like "2 eggs", "3 cup rice", etc.
        
        Args:
            meal_description: Description of the meal
            
        Returns:
            Estimated calorie count or None
        """
        try:
            prompt = f"""Analyze the following meal and calculate total calories.

Meal: "{meal_description}"

Calculate calories for each item. Use the reference values below where applicable, but you can also use your own nutritional knowledge for items not listed:

Reference values (you can use these, but also estimate for other foods based on your knowledge):
- 1 egg = 78 calories
- 1 cup cooked rice = 206 calories
- 1 slice bread = 78 calories
- 100g chicken = 165 calories
- 100g beef = 250 calories
- 100g fish = 100 calories
- 1 cup milk = 150 calories
- 1 medium potato = 160 calories
- 1 cup pasta = 200 calories
- 1 banana = 105 calories
- 1 apple = 95 calories
- 1 cup mixed vegetables = 60-80 calories
- 1 cup cooked vegetables = 80-100 calories
- 1 cup stir-fried vegetables = 100-150 calories
- 1 cup salad = 30-50 calories
- 1 tablespoon oil = 120 calories
- 1 tablespoon butter = 100 calories
- 1 slice cheese = 110 calories

IMPORTANT: If you don't recognize a food item, use your general nutritional knowledge to estimate. For "mixed vegetables" or any vegetable dish, estimate 60-100 calories per cup depending on cooking method.

Respond ONLY in JSON format:
{{
    "breakdown": "X item1: A cal, Y item2: B cal",
    "total_calories": number
}}"""

            response = await self.llm_client.chat.completions.create(
                model=self.settings.groq_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a nutritionist assistant. Calculate calories based on the meal description. Always respond in valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.3,
                max_tokens=200,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            logger.info(f"LLM response: {content}")
            
            data = json.loads(content)
            total = data.get("total_calories")
            
            if total and isinstance(total, (int, float)):
                return int(total)
                
        except Exception as e:
            logger.error(f"Error estimating calories with LLM: {e}")
        
        return None

    async def _search_nutritionix(self, query: str) -> Optional[int]:
        """Search using web scraping (fallback method)."""
        try:
            search_url = f"https://www.google.com/search?q={query}+calories"
            response = self.session.get(search_url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text()

                # Pattern to match common calorie formats
                patterns = [
                    r"(\d+)\s*(?:calories?|cal|kcal)",
                    r"(\d+)\s*cal",
                    r"(\d+)\s*kcal",
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        for match in matches:
                            cal = int(match)
                            if 10 <= cal <= 3000:
                                return cal

        except Exception as e:
            logger.error(f"Error searching nutrition: {e}")

        return None

    def _parse_common_meals(self, meal_description: str) -> Optional[int]:
        """Parse common meal patterns for approximate calorie estimation."""
        meal_lower = meal_description.lower().strip()
        
        # Skip to LLM ONLY if it has explicit quantities with numbers
        # e.g., "2 eggs", "3 cups rice", "100g chicken"
        import re
        # Pattern: number followed by unit of measurement
        quantity_pattern = r'(?:^|\s)\d+\s*(?:cup|cups|piece|pieces|slice|slices|g|gram|grams|kg|oz|ounce|tbsp|tsp|tablespoon|teaspoon|small|medium|large)(?:s|\b)'
        if re.search(quantity_pattern, meal_lower):
            # Has explicit quantity markers - let LLM handle it
            return None
        
        # Common meal calorie estimates (single items or known phrases)
        meal_estimates = {
            # Salads
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

            # Chicken and Meat
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

            # Pasta and Fast Food
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

            # Mexican Food
            "taco": 170,
            "tacos": 300,
            "burrito": 500,
            "quesadilla": 450,
            "nachos": 400,

            # Asian Food
            "sushi": 350,
            "ramen": 450,
            "fried rice": 450,
            "chicken fried rice": 550,
            "stir fry": 400,
            "noodles": 400,
            "chicken noodles": 450,
            "rice bowl": 500,
            "dumplings": 300,

            # Bangladeshi / South Asian Food
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

            # Breakfast
            "boiled egg": 78,
            "fried egg": 120,
            "omelette": 180,
            "scrambled eggs": 180,
            "oatmeal": 150,
            "pancakes": 350,
            "toast": 80,
            "peanut butter toast": 200,
            "cereal with milk": 250,

            # Fruits
            "apple": 95,
            "banana": 105,
            "orange": 62,
            "mango": 100,
            "grapes": 100,
            "watermelon": 85,
            "papaya": 60,
            "pineapple": 80,

            # Snacks
            "almonds": 165,
            "peanuts": 160,
            "yogurt": 150,
            "greek yogurt": 130,
            "protein bar": 200,
            "dark chocolate": 170,
            "popcorn": 100,

            # Soups
            "soup": 250,
            "chicken soup": 180,
            "vegetable soup": 120,
            "tomato soup": 150,

            # Drinks
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

        # First, check for exact match (whole string)
        if meal_lower in meal_estimates:
            logger.info(f"Exact match: '{meal_lower}' with {meal_estimates[meal_lower]} calories")
            return meal_estimates[meal_lower]
        
        # Check for phrase matches (known phrases within the text)
        max_match_length = 0
        best_match = None
        
        for meal, calories in meal_estimates.items():
            # Only match if the phrase is a significant part (not just a substring)
            # and contains multiple words (so we don't match "rice" in "chicken rice")
            if meal in meal_lower:
                phrase_len = len(meal.split())
                if phrase_len >= max_match_length:
                    max_match_length = phrase_len
                    best_match = calories
        
        if best_match:
            logger.info(f"Matched with {best_match} calories")
            return best_match

        return None


# Service instance for dependency injection
web_search_agent = WebSearchAgent()