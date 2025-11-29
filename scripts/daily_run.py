from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.content_generator import ContentGenerator
from automation.image_generator import ImageGenerator
from automation.storage import StorageClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate daily Substack draft and assets.")
    parser.add_argument("--date", type=date.fromisoformat, help="Target date for the draft (YYYY-MM-DD).", default=None)
    parser.add_argument("--skip-images", action="store_true", help="Skip image generation.")
    parser.add_argument("--skip-sheets", action="store_true", help="Skip Google Sheets save.")
    parser.add_argument("--stub", action="store_true", help="Use offline-safe stub content and image files.")
    return parser.parse_args()


def run_for_date(
    target_date: Optional[date] = None, skip_images: bool = False, skip_sheets: bool = False, stub: bool = False
) -> None:
    target_date = target_date or date.today()
    generator = ContentGenerator(use_stub=stub)
    storage = StorageClient()
    bundle = generator.generate(target_date)

    image_paths = None
    if not skip_images:
        image_generator = ImageGenerator(use_stub=stub)
        image_paths = image_generator.create_images(bundle.image_prompts, target_date).image_paths

    markdown_path = storage.save_markdown(bundle, target_date, image_paths)
    if not skip_sheets:
        storage.save_to_sheet(bundle, target_date, image_paths)

    print(f"Draft saved to: {markdown_path}")
    if image_paths:
        print("Images saved:")
        for label, path in image_paths.items():
            print(f"- {label}: {path}")


def main() -> None:
    args = parse_args()
    run_for_date(
        args.date,
        skip_images=args.skip_images,
        skip_sheets=args.skip_sheets,
        stub=args.stub,
    )


if __name__ == "__main__":
    main()
