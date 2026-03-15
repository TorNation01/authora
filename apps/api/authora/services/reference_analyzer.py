"""Text analysis for reference toolkit - repeated phrases, readability."""

import re
from collections import Counter

from authora.services.reference_data import (
    CLICHES,
    OVERUSED_WORDS,
    get_simplification_hint,
    get_vocab_enhancements,
)


def extract_words(text: str) -> list[str]:
    """Extract words from text (lowercase, alphanumeric)."""
    return re.findall(r"\b[a-z0-9']+\b", text.lower())


def extract_phrases(text: str, n: int = 2) -> list[str]:
    """Extract n-word phrases."""
    words = extract_words(text)
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def find_repeated_phrases(text: str, min_count: int = 2, phrase_len: int = 3) -> list[dict]:
    """Find repeated phrases in text."""
    phrases = extract_phrases(text, phrase_len)
    counts = Counter(phrases)
    return [
        {"phrase": p, "count": c}
        for p, c in counts.most_common(20)
        if c >= min_count and len(p) > 5
    ]


def find_overused_words(text: str) -> list[dict]:
    """Find overused words in text."""
    words = extract_words(text)
    counts = Counter(words)
    return [
        {"word": w, "count": c}
        for w, c in counts.most_common()
        if w in OVERUSED_WORDS and c >= 2
    ]


def find_cliches(text: str) -> list[dict]:
    """Find cliches in text."""
    lower = text.lower()
    found = []
    for cliche in CLICHES:
        if cliche in lower:
            found.append({"phrase": cliche})
    return found


def readability_hints(text: str) -> list[dict]:
    """Suggest simpler alternatives for complex words."""
    words = extract_words(text)
    hints = []
    seen = set()
    for w in words:
        if w in seen:
            continue
        simpler = get_simplification_hint(w)
        if simpler:
            hints.append({"word": w, "suggestion": simpler})
            seen.add(w)
    return hints


def vocab_enhancement_hints(text: str) -> list[dict]:
    """Suggest richer vocabulary for common words."""
    words = extract_words(text)
    hints = []
    seen = set()
    for w in words:
        if w in seen:
            continue
        alternatives = get_vocab_enhancements(w)
        if alternatives:
            hints.append({"word": w, "alternatives": alternatives[:5]})
            seen.add(w)
    return hints


def analyze_text(text: str) -> dict:
    """Full text analysis for reference panel."""
    return {
        "repeated_phrases": find_repeated_phrases(text),
        "overused_words": find_overused_words(text),
        "cliches": find_cliches(text),
        "readability_hints": readability_hints(text),
        "vocab_enhancements": vocab_enhancement_hints(text),
    }
