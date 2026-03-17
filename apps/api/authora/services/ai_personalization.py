"""AI personalization service - build style context for prompts."""

import re
from typing import Any


def derive_style_from_content(text: str, max_chars: int = 15000) -> dict[str, str | None]:
    """
    Derive a simple style profile from user content (tone, vocabulary, sentence structure).

    Lightweight heuristics: sentence length, contractions (casual vs formal),
    paragraph length. Returns dict with voice, tone, vocabulary, sentence_style.
    """
    if not text or not text.strip():
        return {"voice": None, "tone": None, "vocabulary": None, "sentence_style": None}

    sample = text.strip()[:max_chars]
    sentences = re.split(r"[.!?]+", sample)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r"\b\w+\b", sample.lower())

    # Sentence structure
    avg_len = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    if avg_len < 12:
        sentence_style = "Short, punchy sentences"
    elif avg_len > 22:
        sentence_style = "Flowing, longer sentences"
    else:
        sentence_style = "Varied sentence length"

    # Tone hint (contractions = more casual)
    contraction_count = sum(1 for w in words if "'" in w or w in ("don't", "won't", "can't", "it's", "that's"))
    total = len(words) or 1
    if contraction_count / total > 0.02:
        tone = "Conversational, casual"
    elif any(w in words for w in ("therefore", "however", "furthermore", "consequently")):
        tone = "Formal, academic"
    else:
        tone = "Balanced"

    return {
        "voice": None,  # User can fill manually
        "tone": tone,
        "vocabulary": None,  # Could add word diversity metric
        "sentence_style": sentence_style,
    }


def build_personalization_context(personalization: dict[str, Any] | None) -> str:
    """
    Build a compact context string for AI prompts from personalization settings.

    Used only when personalization is enabled. Instructs AI to enhance, not replace,
    and to maintain the user's voice.
    """
    if not personalization or not personalization.get("enabled"):
        return ""

    parts: list[str] = []

    # Core principle: AI enhances, maintains voice, optional
    parts.append(
        "PERSONALIZATION (optional): Adapt to the author's style. Enhance, do not replace. "
        "Maintain the author's voice. Suggestions should feel like the author wrote them."
    )

    tone_prefs = personalization.get("tone_preferences")
    if tone_prefs and isinstance(tone_prefs, list) and len(tone_prefs) > 0:
        tones = ", ".join(str(t) for t in tone_prefs[:5])
        parts.append(f"Preferred tone(s): {tones}.")

    style_profile = personalization.get("style_profile")
    if style_profile and isinstance(style_profile, dict):
        sp_parts: list[str] = []
        if style_profile.get("voice"):
            sp_parts.append(f"Voice: {style_profile['voice']}")
        if style_profile.get("tone"):
            sp_parts.append(f"Tone: {style_profile['tone']}")
        if style_profile.get("vocabulary"):
            sp_parts.append(f"Vocabulary: {style_profile['vocabulary']}")
        if style_profile.get("sentence_style"):
            sp_parts.append(f"Sentence style: {style_profile['sentence_style']}")
        if sp_parts:
            parts.append("Style profile: " + "; ".join(sp_parts))

    return "\n".join(parts)
