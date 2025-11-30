from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import time
from pathlib import Path
from typing import Optional


DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
ASSET_DIR = Path(os.getenv("ASSET_DIR", "assets"))
HISTORY_PATH = DATA_DIR / "topics_history.json"


@dataclass(frozen=True)
class ScheduleConfig:
    """Configuration for the daily scheduler."""

    run_hour: int = int(os.getenv("RUN_HOUR", 7))
    run_minute: int = int(os.getenv("RUN_MINUTE", 0))
    tz: str = os.getenv("RUN_TIMEZONE", "America/New_York")

    @property
    def as_time(self) -> time:
        return time(self.run_hour, self.run_minute)


@dataclass(frozen=True)
class OpenAIConfig:
    """Settings for the OpenAI client."""

    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    image_model: str = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")


@dataclass(frozen=True)
class SheetsConfig:
    """Google Sheets integration settings."""

    spreadsheet_id: Optional[str] = os.getenv("GOOGLE_SHEET_ID")
    service_account_json: Optional[str] = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    worksheet_name: str = os.getenv("GOOGLE_WORKSHEET_NAME", "Daily Drafts")

    def has_credentials(self) -> bool:
        return bool(self.spreadsheet_id and self.service_account_json)


@dataclass(frozen=True)
class ContentConfig:
    """Parameters controlling generation content and tone."""

    teaser_length: int = int(os.getenv("TEASER_LENGTH", 200))
    min_post_words: int = int(os.getenv("MIN_POST_WORDS", 400))


SCHEDULE_CONFIG = ScheduleConfig()
OPENAI_CONFIG = OpenAIConfig()
SHEETS_CONFIG = SheetsConfig()
CONTENT_CONFIG = ContentConfig()

# Ensure core directories exist for local storage/fallbacks.
DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSET_DIR.mkdir(parents=True, exist_ok=True)
