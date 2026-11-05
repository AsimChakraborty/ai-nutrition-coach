"""FastAPI application for the Nutrition Coach."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings, setup_logging
from app.routers import nutrition_router

# Setup logging with file output
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Nutrition Coach API...")
    settings = get_settings()

    if settings.is_groq_configured:
        logger.info("Groq API is configured")
    else:
        logger.warning("Groq API key not configured - using fallback suggestions")

    if settings.is_google_sheets_configured:
        logger.info("Google Sheets is configured")
    else:
        logger.warning("Google Sheets not configured - using fallback logging")

    yield

    logger.info("Shutting down Nutrition Coach API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="""
        🍎 AI-Powered Nutrition Coach

        An intelligent nutrition assistant that helps you track meals and get healthy suggestions.

        ## Features

        * **Log Meals** - Submit what you ate and get calorie estimates
        * **Meal History** - View your meal history
        * **Smart Suggestions** - Get AI-powered healthy meal recommendations using Groq

        ## Workflow

        1. Submit a meal through the API
        2. Web Search Agent estimates calories
        3. Logger Agent records the entry
        4. Get a healthy follow-up meal suggestion
        """,
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For development; restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(nutrition_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )