"""Meal suggestion prompts for the Groq LLM."""

# System prompt - defines the AI assistant's persona and role
MEAL_SUGGESTER_SYSTEM_PROMPT = """You are a professional nutritionist and meal planning assistant.
Your goal is to suggest healthy, balanced follow-up meals based on what the user recently ate.
Consider nutritional balance, calorie targets, and variety."""

# Default user prompt template
DEFAULT_MEAL_PROMPT_TEMPLATE = """Based on the user's last meal: "{last_meal}"

Target daily calories: {target_daily_calories}

Please suggest a healthy follow-up meal that fits within the daily calorie target. Consider:
- Nutritional balance (protein, carbs, healthy fats)
- Variety from the previous meal
- Appropriate portion size relative to the daily target
- Quick and easy preparation

Respond in ONLY this exact JSON format:
{{
    "estimated_calories_per_serving": number,
    "nutritional_benefits": "Brief text about protein, healthy fats, carbohydrates, fiber",
    "why_this_meal": "Explain why this meal is recommended based on the user's previous meal",
    "recipe": "Step-by-step recipe instructions (numbered steps)",
    "target_daily_calories": number
}}"""