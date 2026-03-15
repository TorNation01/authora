"""Readability scoring (Flesch-Kincaid, etc.)."""

import re

from authora.services.editing.text_utils import extract_sentences


def _count_syllables(word: str) -> int:
    """Approximate syllable count for readability (English)."""
    import re
    word = word.lower()
    if len(word) <= 3:
        return 1
    word = re.sub(r"(?:es|ed)$", "", word)
    vowels = re.findall(r"[aeiouy]+", word)
    return max(1, len(vowels))


def analyze_readability(text: str) -> dict:
    """
    Analyze readability. Returns Flesch Reading Ease, grade level, and metrics.
    """
    if not text or not text.strip():
        return {
            "flesch_reading_ease": 0,
            "flesch_kincaid_grade": 0,
            "sentence_count": 0,
            "word_count": 0,
            "syllable_count": 0,
            "avg_sentence_length": 0,
            "avg_syllables_per_word": 0,
            "grade_label": "N/A",
        }

    sentences = extract_sentences(text)
    words = text.split()
    sentence_count = len(sentences)
    word_count = len(words)
    syllable_count = sum(_count_syllables(w) for w in words)

    if sentence_count == 0 or word_count == 0:
        return {
            "flesch_reading_ease": 0,
            "flesch_kincaid_grade": 0,
            "sentence_count": 0,
            "word_count": word_count,
            "syllable_count": syllable_count,
            "avg_sentence_length": 0,
            "avg_syllables_per_word": 0,
            "grade_label": "N/A",
        }

    avg_sentence_length = word_count / sentence_count
    avg_syllables_per_word = syllable_count / word_count

    # Flesch Reading Ease: 206.835 - 1.015(words/sentences) - 84.6(syllables/words)
    flesch = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    flesch = max(0, min(100, round(flesch, 1)))

    # Flesch-Kincaid Grade Level
    fk = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
    fk = max(0, round(fk, 1))

    grade_labels = {
        0: "Pre-school",
        1: "1st grade",
        2: "2nd grade",
        3: "3rd grade",
        4: "4th grade",
        5: "5th grade",
        6: "6th grade",
        7: "7th grade",
        8: "8th grade",
        9: "9th grade",
        10: "10th grade",
        11: "11th grade",
        12: "12th grade",
    }
    grade_label = grade_labels.get(int(fk), f"College ({int(fk)}+)")

    return {
        "flesch_reading_ease": flesch,
        "flesch_kincaid_grade": fk,
        "sentence_count": sentence_count,
        "word_count": word_count,
        "syllable_count": syllable_count,
        "avg_sentence_length": round(avg_sentence_length, 1),
        "avg_syllables_per_word": round(avg_syllables_per_word, 2),
        "grade_label": grade_label,
    }
