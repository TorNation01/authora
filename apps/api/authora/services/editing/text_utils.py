"""Text extraction utilities for editing engine."""

import re

from authora.services.export import tiptap_to_plain_text


def extract_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    if not text or not text.strip():
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in parts if s.strip()]


def extract_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    if not text or not text.strip():
        return []
    # Split on sentence boundaries (. ! ?) followed by space or end
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in parts if s.strip()]


def count_syllables(word: str) -> int:
    """Approximate syllable count for readability (English)."""
    word = word.lower()
    if len(word) <= 3:
        return 1
    word = re.sub(r"(?:es|ed)$", "", word)
    vowels = re.findall(r"[aeiouy]+", word)
    return max(1, len(vowels))
