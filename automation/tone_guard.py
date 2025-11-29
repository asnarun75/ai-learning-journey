from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence


DEFAULT_BLOCKLIST: Sequence[str] = (
    "election",
    "politics",
    "campaign",
    "protest",
    "vote",
    "partisan",
    "left-wing",
    "right-wing",
    "government scandal",
    "conflict",
    "war",
    "controversy",
)

DEFAULT_TONE_NOTES: Sequence[str] = (
    "first-person reflections",
    "sensory details from daily meditation and yoga",
    "apolitical and inclusive language",
    "humble, conversational tone",
    "references to Indian traditions without making health claims",
)


class BlocklistError(ValueError):
    """Raised when generated text includes blocked content."""


@dataclass
class ToneGuard:
    blocklist: Sequence[str] = DEFAULT_BLOCKLIST
    tone_notes: Sequence[str] = DEFAULT_TONE_NOTES

    def ensure_safe(self, text: str) -> str:
        lower = text.lower()
        for term in self.blocklist:
            if re.search(rf"\b{re.escape(term)}\b", lower):
                raise BlocklistError(f"Blocked term detected: {term}")
        return text

    def add_voice_notes(self, prompt: str) -> str:
        notes = "\n".join(f"- {note}" for note in self.tone_notes)
        return f"{prompt}\n\nVoice & authenticity notes:\n{notes}\nAvoid political topics entirely."

    def soften_phrasing(self, text: str) -> str:
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        edited: List[str] = []
        for sentence in sentences:
            if len(sentence) > 180:
                midpoint = len(sentence) // 2
                sentence = sentence[:midpoint].strip() + ", and " + sentence[midpoint:].strip()
            edited.append(sentence)
        refined = ". ".join(edited)
        if refined and not refined.endswith("."):
            refined += "."
        return refined

    def polish(self, text: str) -> str:
        return self.ensure_safe(self.soften_phrasing(text))

    def validate_all(self, texts: Iterable[str]) -> None:
        for text in texts:
            self.ensure_safe(text)
