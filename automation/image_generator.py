from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - runtime fallback for stub mode
    OpenAI = None  # type: ignore[assignment]

from .config import ASSET_DIR, OPENAI_CONFIG


@dataclass
class ImageResult:
    image_paths: Dict[str, Path]


class ImageGenerator:
    def __init__(
        self,
        output_dir: Path = ASSET_DIR,
        openai_client: Optional[OpenAI] = None,
        use_stub: bool = False,
    ) -> None:
        self.output_dir = output_dir
        self.stub_mode = use_stub or not OPENAI_CONFIG.api_key
        if self.stub_mode:
            self.client = None
        else:
            if OpenAI is None:
                raise ImportError("Install openai or run with stub mode enabled.")
            self.client = openai_client or OpenAI(api_key=OPENAI_CONFIG.api_key)

    def _ensure_dir(self, target_date: date) -> Path:
        day_dir = self.output_dir / target_date.isoformat()
        day_dir.mkdir(parents=True, exist_ok=True)
        return day_dir

    def _generate_image(self, prompt: str) -> bytes:
        if self.stub_mode:
            return prompt.encode("utf-8")
        if not OPENAI_CONFIG.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for image generation.")
        response = self.client.images.generate(
            model=OPENAI_CONFIG.image_model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
        )
        base64_image = response.data[0].b64_json
        return base64.b64decode(base64_image)

    def create_images(self, prompts: Dict[str, str], target_date: Optional[date] = None) -> ImageResult:
        target_date = target_date or date.today()
        day_dir = self._ensure_dir(target_date)
        image_paths: Dict[str, Path] = {}
        for label, prompt in prompts.items():
            image_bytes = self._generate_image(prompt)
            filename = f"{label}.{'txt' if self.stub_mode else 'png'}"
            image_path = day_dir / filename
            with image_path.open("wb") as img_file:
                img_file.write(image_bytes)
            image_paths[label] = image_path
        return ImageResult(image_paths=image_paths)
