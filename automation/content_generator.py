from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - runtime fallback for stub mode
    OpenAI = None  # type: ignore[assignment]

from .config import CONTENT_CONFIG, HISTORY_PATH, OPENAI_CONFIG
from .tone_guard import ToneGuard


DEFAULT_THEMES: List[str] = [
    "Mindful morning rituals inspired by Ayurveda",
    "Walking meditations in nearby parks",
    "Cooking simple sattvic meals",
    "Gentle yoga for busy workdays",
    "Gratitude journaling before bed",
    "Breathwork to reset between meetings",
    "Tea ceremonies as a pause",
    "Digital minimalism evenings",
    "Compassion meditations for colleagues and family",
    "Nature-inspired affirmations",
    "Unplugged weekends",
    "Bedtime storytelling traditions",
    "Chanting and mantra practice",
    "Grounding through barefoot walks",
    "Acts of quiet service",
    "Sacred spaces at home",
    "Mindful commuting",
    "Slow cooking as evening meditation",
    "Mindful use of social media",
    "Rest day reflections",
    "Breath-led stretching",
    "Light routines before sunrise",
    "Journaling with incense and calm music",
    "Water as a mindful companion",
    "Evening gratitude walks",
    "Silence sprints during the day",
    "Micro-meditations between tasks",
    "Weekly ritual of decluttering",
    "Listening to classical Indian music",
    "Sunday planning with intention",
]


@dataclass
class ContentBundle:
    topic: str
    title: str
    subtitle: str
    long_post: str
    teaser: str
    image_prompts: Dict[str, str]


class ContentGenerator:
    def __init__(
        self,
        history_path: Path = HISTORY_PATH,
        openai_client: Optional[OpenAI] = None,
        tone_guard: Optional[ToneGuard] = None,
        use_stub: bool = False,
    ) -> None:
        self.history_path = history_path
        self.themes = DEFAULT_THEMES.copy()
        self.tone_guard = tone_guard or ToneGuard()
        self.stub_mode = use_stub or not OPENAI_CONFIG.api_key
        if self.stub_mode:
            self.client = None
        else:
            if OpenAI is None:
                raise ImportError("Install openai or run with stub mode enabled.")
            self.client = openai_client or OpenAI(api_key=OPENAI_CONFIG.api_key)
        self._history = self._load_history()

    def _load_history(self) -> List[str]:
        if self.history_path.exists():
            with self.history_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        return []

    def _save_history(self) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("w", encoding="utf-8") as handle:
            json.dump(self._history, handle, indent=2)

    def _choose_theme(self) -> str:
        available = [t for t in self.themes if t not in self._history]
        if not available:
            self._history = []
            available = self.themes.copy()
        theme = random.choice(available)
        self._history.append(theme)
        self._save_history()
        return theme

    def _build_prompt(self, theme: str, target_date: date) -> str:
        base_prompt = f"""
        Create a Substack draft for a wholesome living blog.
        Audience: curious readers seeking calm habits and gentle inspiration.
        Date: {target_date.isoformat()}.
        Theme: {theme}.

        Produce:
        1) Catchy, authentic title that avoids clickbait.
        2) Subtitle with a grounding promise.
        3) Long-form post of at least {CONTENT_CONFIG.min_post_words} words.
        4) Short teaser of about {CONTENT_CONFIG.teaser_length} characters for Substack Notes/Instagram.
        5) Three safe image prompts: main cover, background, thumbnail.

        Respond using these labeled sections with blank lines between them so paragraphs inside "Long Post" stay intact:
        Title:
        Subtitle:
        Long Post:
        Teaser:
        Main Image:
        Background Image:
        Thumbnail Image:
        """
        return self.tone_guard.add_voice_notes(base_prompt)

    def _call_model(self, prompt: str) -> str:
        if not OPENAI_CONFIG.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for generation.")
        completion = self.client.responses.create(
            model=OPENAI_CONFIG.model,
            input=prompt,
        )
        return completion.output[0].content[0].text

    def _parse_response(self, response: str) -> ContentBundle:
        marker_pattern = re.compile(
            r"^(?P<label>(?:Title|Subtitle|Long Post|Long-Form Post|Teaser|Main Image|Background Image|Thumbnail Image)):\\s*(?P<value>.*?)(?=^(?:Title|Subtitle|Long Post|Long-Form Post|Teaser|Main Image|Background Image|Thumbnail Image):|\\Z)",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        captured = {match.group("label").lower(): match.group("value").strip() for match in marker_pattern.finditer(response)}

        if captured:
            title = captured.get("title")
            subtitle = captured.get("subtitle")
            long_post = captured.get("long post") or captured.get("long-form post")
            teaser = captured.get("teaser")
            image_prompts = {
                "main": captured.get("main image", ""),
                "background": captured.get("background image", ""),
                "thumbnail": captured.get("thumbnail image", ""),
            }
            if not all([title, subtitle, long_post, teaser]):
                raise ValueError("Model response missing required labeled sections.")
        else:
            sections = [part.strip(" \n#-") for part in response.split("\n\n") if part.strip()]
            if len(sections) < 7:
                raise ValueError("Model response missing sections for fallback parsing.")

            title, subtitle = sections[0], sections[1]
            teaser = sections[-4]
            image_blocks = sections[-3:]
            long_post_blocks = sections[2:-4]
            if not long_post_blocks:
                raise ValueError("Model response missing long post content.")
            long_post = "\n\n".join(long_post_blocks)
            labels = ["main", "background", "thumbnail"]
            image_prompts = {label: block for label, block in zip(labels, image_blocks)}

        self.tone_guard.validate_all([title, subtitle, long_post, teaser, *image_prompts.values()])
        return ContentBundle(
            topic=title,
            title=title,
            subtitle=subtitle,
            long_post=self.tone_guard.polish(long_post),
            teaser=self.tone_guard.polish(teaser),
            image_prompts=image_prompts,
        )

    def generate(self, target_date: Optional[date] = None) -> ContentBundle:
        target_date = target_date or date.today()
        theme = self._choose_theme()
        if self.stub_mode:
            return self._generate_stub_bundle(theme, target_date)

        prompt = self._build_prompt(theme, target_date)
        raw = self._call_model(prompt)
        bundle = self._parse_response(raw)
        return ContentBundle(
            topic=theme,
            title=bundle.title,
            subtitle=bundle.subtitle,
            long_post=bundle.long_post,
            teaser=bundle.teaser,
            image_prompts=bundle.image_prompts,
        )

    def _generate_stub_bundle(self, theme: str, target_date: date) -> ContentBundle:
        """Offline-friendly fallback for testing without OpenAI credentials."""

        intro = (
            "I’ve been easing back into my morning rhythm—sitting with the breath, sipping warm ginger tea, and"
            " letting the day rise gently."
        )
        body = (
            "The theme for today is {theme}. I share a small reflection from my Indian meditative practice,"
            " what it feels like to keep the pace slow, and how I weave a little service into the routine."
            " These notes are deliberately calm and apolitical, meant to feel like a handwritten letter."
        )
        closing = (
            "May this invite you to pause, breathe, and choose one soft habit before the day rushes in."
        )
        long_post = f"{intro} {body.format(theme=theme)} {closing}"
        polished_long = self.tone_guard.polish(long_post)
        teaser = self.tone_guard.polish(
            "A gentle check-in on mindful living, rooted in Indian meditation and simple service."
        )
        image_prompts = {
            "main": f"Calm morning scene reflecting {theme}, soft dawn light, minimalist, serene.",
            "background": "Soft watercolor texture with warm sunrise hues, subtle and uncluttered.",
            "thumbnail": "Simple line art of a meditating figure with a cup of tea, friendly and quiet.",
        }
        self.tone_guard.validate_all([polished_long, teaser, *image_prompts.values()])
        return ContentBundle(
            topic=theme,
            title=f"{theme} — a simple practice",
            subtitle=f"A calm note for {target_date.isoformat()}",
            long_post=polished_long,
            teaser=teaser,
            image_prompts=image_prompts,
        )
