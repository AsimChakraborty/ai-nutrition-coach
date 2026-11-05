"""Streamlit frontend for the Nutrition Coach application."""

import logging
import sys
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import get_settings, setup_logging

# Setup logging with file output
setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()
API_BASE_URL = f"http://localhost:{settings.port}"


def check_api_health() -> bool:
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/nutrition/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def log_meal_api(user_name: str, meal_description: str) -> dict:
    """Call the API to log a meal."""
    response = requests.post(
        f"{API_BASE_URL}/api/nutrition/log",
        params={"user_name": user_name, "meal_description": meal_description},
    )
    response.raise_for_status()
    return response.json()


def get_meal_suggestion_api(user_name: str, last_meal: str, target_calories: int = 2000) -> dict:
    """Call the API to get a meal suggestion."""
    response = requests.post(
        f"{API_BASE_URL}/api/nutrition/suggest",
        json={"user_name": user_name, "last_meal": last_meal, "target_daily_calories": target_calories},
    )
    response.raise_for_status()
    return response.json()
def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="Nutrition Coach", page_icon="🍎", layout="wide")

    st.title("AI-Powered Nutrition Coach")
    st.markdown("Track your meals and get healthy suggestions!")

    with st.sidebar:
        st.header("👤 User Settings")
        user_name = st.text_input("Your Name", value="John")
        target_calories = st.slider("Target Daily Calories", 1200, 3500, 2000, 100)
        st.divider()
        st.subheader("🔧 API Status")
        if check_api_health():
            st.success("API Connected")
        else:
            st.error("API Not Connected")

    tab1, tab2 = st.tabs(["📝 Log Meal", "💡 Get Suggestion"])

    with tab1:
        st.header("Log Your Meal")
        meal_description = st.text_input("What did you eat?", placeholder="e.g., chicken salad")
        if st.button("Log Meal", type="primary"):
            if user_name and meal_description:
                with st.spinner("Processing..."):
                    try:
                        result = log_meal_api(user_name, meal_description)
                        st.success("Meal logged!")
                        st.metric("Calories", result.get("estimated_calories", "N/A"))
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab2:
        st.header("Get a Healthy Suggestion")
        last_meal = st.text_area("What did you last eat?", height=100)
        if st.button("Get Suggestion", type="primary"):
            if user_name and last_meal:
                with st.spinner("Generating suggestion..."):
                    try:
                        suggestion = get_meal_suggestion_api(user_name, last_meal, target_calories)
                        st.success("Here's your suggestion!")
                        
                        # Display calories
                        st.metric("Estimated Calories", f"{suggestion['estimated_calories_per_serving']} kcal per serving")
                        
                        # Display nutritional benefits
                        st.markdown("### 🥗 Nutritional Benefits")
                        st.markdown(suggestion["nutritional_benefits"])
                        
                        # Display why this meal
                        st.info(f"💡 **Why this meal?**\n\n{suggestion['why_this_meal']}")
                        
                        # Display recipe in an expandable section
                        with st.expander("📖 View Recipe", expanded=True):
                            st.markdown(suggestion["recipe"])
                    except Exception as e:
                        st.error(f"Error: {e}")


if __name__ == "__main__":
    main()