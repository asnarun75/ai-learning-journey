from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, Optional

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:  # pragma: no cover - allows offline stub runs
    gspread = None  # type: ignore[assignment]
    Credentials = None  # type: ignore[assignment]

from .config import DATA_DIR, SHEETS_CONFIG
from .content_generator import ContentBundle

SCOPE = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
)


class StorageClient:
    def __init__(self, worksheet_name: Optional[str] = None) -> None:
        self.worksheet_name = worksheet_name or SHEETS_CONFIG.worksheet_name

    def _get_sheet(self):
        if not SHEETS_CONFIG.has_credentials() or not gspread or not Credentials:
            return None
        service_account_info = json.loads(SHEETS_CONFIG.service_account_json)  # type: ignore[arg-type]
        creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPE)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SHEETS_CONFIG.spreadsheet_id)
        try:
            worksheet = spreadsheet.worksheet(self.worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=self.worksheet_name, rows=200, cols=15)
            worksheet.append_row(
                [
                    "Date",
                    "Theme",
                    "Title",
                    "Subtitle",
                    "Long Post",
                    "Teaser",
                    "Cover Image",
                    "Background Image",
                    "Thumbnail",
                    "Status",
                    "Review Checklist",
                ]
            )
        return worksheet

    def save_to_sheet(self, bundle: ContentBundle, target_date: date, image_paths: Optional[Dict[str, Path]] = None) -> None:
        worksheet = self._get_sheet()
        if not worksheet:
            return
        image_paths = image_paths or {}
        worksheet.append_row(
            [
                target_date.isoformat(),
                bundle.topic,
                bundle.title,
                bundle.subtitle,
                bundle.long_post,
                bundle.teaser,
                str(image_paths.get("main", "")),
                str(image_paths.get("background", "")),
                str(image_paths.get("thumbnail", "")),
                "Draft",
                "Tone / Authenticity / No politics / Image OK",
            ]
        )

    def save_markdown(self, bundle: ContentBundle, target_date: date, image_paths: Optional[Dict[str, Path]] = None) -> Path:
        image_paths = image_paths or {}
        target_dir = DATA_DIR / "drafts"
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / f"{target_date.isoformat()}.md"
        with file_path.open("w", encoding="utf-8") as file:
            file.write(f"# {bundle.title}\n")
            file.write(f"## {bundle.subtitle}\n\n")
            file.write(f"*Date:* {target_date.isoformat()}\n")
            file.write(f"*Theme:* {bundle.topic}\n\n")
            file.write(bundle.long_post + "\n\n")
            file.write(f"**Teaser:** {bundle.teaser}\n\n")
            if image_paths:
                file.write("## Images\n")
                for label, path in image_paths.items():
                    file.write(f"- {label}: {path}\n")
        return file_path
