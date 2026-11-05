"""Logger service for recording meal entries to CSV file."""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from config.settings import get_settings
from app.models.nutrition import MealEntry, MealEntryResponse

logger = logging.getLogger(__name__)


class LoggerAgent:
    """Agent that logs meal entries to a CSV file."""

    def __init__(self) -> None:
        """Initialize the logger agent."""
        self.settings = get_settings()
        
        # CSV file path
        self.csv_path = self.settings.project_root / "data" / "meal_log.csv"
        self._ensure_csv_exists()

    def _ensure_csv_exists(self) -> None:
        """Ensure the CSV file and data directory exist."""
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.csv_path.exists():
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'user_name', 'meal_description', 'estimated_calories', 'timestamp'])

    def _get_next_id(self) -> int:
        """Get the next available ID for the CSV file."""
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if rows:
                    return max(int(row['id']) for row in rows) + 1
        except Exception:
            pass
        return 1

    async def log_entry(
        self,
        user_name: str,
        meal_description: str,
        estimated_calories: Optional[int] = None,
    ) -> MealEntryResponse:
        """
        Log a meal entry to CSV file.

        Args:
            user_name: Name of the user
            meal_description: Description of the meal
            estimated_calories: Estimated calorie count (optional)

        Returns:
            MealEntryResponse with the logged entry details
        """
        logger.info(f"Logging meal for user {user_name}: {meal_description}")

        timestamp = datetime.utcnow()
        entry_id = self._get_next_id()

        # Create entry
        entry = MealEntry(
            user_name=user_name,
            meal_description=meal_description,
            estimated_calories=estimated_calories,
            timestamp=timestamp,
        )

        # Save to CSV
        self._save_to_csv(entry, entry_id)

        logger.info(f"Saved meal to CSV: {entry_id}")

        return MealEntryResponse(
            id=entry_id,
            user_name=entry.user_name,
            meal_description=entry.meal_description,
            estimated_calories=entry.estimated_calories,
            timestamp=entry.timestamp.isoformat(),
        )

    def _save_to_csv(self, entry: MealEntry, entry_id: int) -> None:
        """Save entry to CSV file."""
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                entry_id,
                entry.user_name,
                entry.meal_description,
                entry.estimated_calories or '',
                entry.timestamp.isoformat(),
            ])

    async def get_history(self, user_name: str) -> List[MealEntryResponse]:
        """
        Get meal history for a user.

        Args:
            user_name: Name of the user

        Returns:
            List of meal entries
        """
        logger.info(f"Getting history for user: {user_name}")
        
        history = []
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['user_name'] == user_name:
                        history.append(MealEntryResponse(
                            id=int(row['id']),
                            user_name=row['user_name'],
                            meal_description=row['meal_description'],
                            estimated_calories=int(row['estimated_calories']) if row['estimated_calories'] else None,
                            timestamp=row['timestamp'],
                        ))
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
        
        return history


# Service instance for dependency injection
logger_agent = LoggerAgent()