"""Pattern-based analysis: filler words, passive voice, repeated phrases."""

import re
from collections import Counter

from authora.services.editing.text_utils import extract_sentences

# Common filler words (expandable)
FILLER_WORDS = {
    "just", "really", "very", "quite", "actually", "basically", "literally",
    "honestly", "simply", "somehow", "perhaps", "maybe", "probably",
    "actually", "definitely", "absolutely", "certainly", "obviously",
    "well", "so", "like", "you know", "i mean", "kind of", "sort of",
    "thing", "things", "stuff", "something", "anything", "everything",
}

# Passive voice patterns: "was/were/been/being + past participle"
PASSIVE_PATTERN = re.compile(
    r"\b(?:was|were|been|being|is|are|am)\s+"
    r"(?:[a-z]+ed|broken|written|given|taken|made|done|seen|known|said)\b",
    re.IGNORECASE,
)


def detect_filler_words(text: str) -> list[dict]:
    """Detect filler words with positions."""
    if not text:
        return []
    text_lower = text.lower()
    words = re.findall(r"\b[\w']+\b", text_lower)
    results = []
    pos = 0
    for i, w in enumerate(words):
        if w in FILLER_WORDS:
            start = text_lower.find(w, pos)
            if start >= 0:
                end = start + len(w)
                results.append({
                    "word": w,
                    "position": start,
                    "count": 1,
                })
                pos = end
    # Aggregate by word
    by_word: dict[str, list] = {}
    for r in results:
        w = r["word"]
        if w not in by_word:
            by_word[w] = []
        by_word[w].append(r["position"])
    return [
        {"word": w, "count": len(positions), "positions": positions[:10]}
        for w, positions in sorted(by_word.items(), key=lambda x: -len(x[1]))
    ]


def detect_passive_voice(text: str) -> list[dict]:
    """Detect passive voice constructions."""
    if not text:
        return []
    sentences = extract_sentences(text)
    results = []
    for i, sent in enumerate(sentences):
        for m in PASSIVE_PATTERN.finditer(sent):
            results.append({
                "sentence": sent[:80] + "..." if len(sent) > 80 else sent,
                "match": m.group(),
                "position": m.start(),
                "sentence_index": i,
            })
    return results[:20]


def detect_repeated_phrases(text: str, min_length: int = 3) -> list[dict]:
    """Detect repeated words or short phrases."""
    if not text:
        return []
    words = re.findall(r"\b[\w']+\b", text.lower())
    # Single word repetition
    word_counts = Counter(words)
    repeated = [
        {"phrase": w, "count": c}
        for w, c in word_counts.most_common(30)
        if c >= 3 and len(w) > 2 and w not in {"the", "and", "to", "of", "a", "in", "is", "it", "for", "that", "with", "on", "as", "was", "be", "have", "has", "had", "this", "from", "or", "by", "one", "are", "but", "not", "they", "we", "you", "he", "she", "his", "her", "their"}
    ]
    return repeated[:15]


def analyze_sentence_length(text: str) -> dict:
    """Analyze sentence length distribution."""
    if not text:
        return {
            "sentences": [],
            "avg_length": 0,
            "min_length": 0,
            "max_length": 0,
            "variance": 0,
            "balance_score": 0,
            "issues": [],
        }
    sentences = extract_sentences(text)
    if not sentences:
        return {
            "sentences": [],
            "avg_length": 0,
            "min_length": 0,
            "max_length": 0,
            "variance": 0,
            "balance_score": 0,
            "issues": [],
        }
    lengths = [len(s.split()) for s in sentences]
    avg = sum(lengths) / len(lengths)
    variance = sum((x - avg) ** 2 for x in lengths) / len(lengths) if lengths else 0
    min_len = min(lengths)
    max_len = max(lengths)

    # Balance: prefer moderate variance; very high = choppy or run-on mix
    balance_score = max(0, 100 - (variance ** 0.5) * 2)

    issues = []
    if max_len > 40:
        issues.append("Some sentences are very long (40+ words). Consider breaking them up.")
    if min_len < 5 and len([l for l in lengths if l < 5]) > len(lengths) / 3:
        issues.append("Many short sentences may feel choppy. Vary rhythm.")
    if variance > 400:
        issues.append("Sentence length varies widely. Consider more consistent rhythm.")

    return {
        "sentences": [{"length": l, "preview": s[:60] + "..." if len(s) > 60 else s} for s, l in zip(sentences[:20], lengths[:20])],
        "avg_length": round(avg, 1),
        "min_length": min_len,
        "max_length": max_len,
        "variance": round(variance, 1),
        "balance_score": round(balance_score, 1),
        "issues": issues,
    }
