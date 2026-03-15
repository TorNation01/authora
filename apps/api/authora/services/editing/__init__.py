"""Editing and polish engine."""

from authora.services.editing.text_utils import tiptap_to_plain_text, extract_sentences
from authora.services.editing.readability import analyze_readability
from authora.services.editing.patterns import (
    detect_filler_words,
    detect_passive_voice,
    detect_repeated_phrases,
    analyze_sentence_length,
)
from authora.services.editing.engine import (
    run_chapter_analysis,
    run_book_analysis,
    build_chapter_scorecard,
    build_manuscript_health,
)

__all__ = [
    "tiptap_to_plain_text",
    "extract_sentences",
    "analyze_readability",
    "detect_filler_words",
    "detect_passive_voice",
    "detect_repeated_phrases",
    "analyze_sentence_length",
    "run_chapter_analysis",
    "run_book_analysis",
    "build_chapter_scorecard",
    "build_manuscript_health",
]
