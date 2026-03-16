"""Default checklist templates for revision pass types."""

REVISION_PASS_LABELS: dict[str, str] = {
    "structural": "Structural pass",
    "clarity": "Clarity pass",
    "pacing": "Pacing pass",
    "emotional_depth": "Emotional depth pass",
    "consistency": "Consistency pass",
    "grammar_polish": "Grammar and polish pass",
    "custom": "Custom pass",
}

DEFAULT_CHECKLISTS: dict[str, list[str]] = {
    "structural": [
        "Does each scene/chapter advance the plot or character?",
        "Are there any scenes that can be cut or merged?",
        "Does the opening hook and the ending satisfy?",
        "Is the story structure clear (setup, conflict, resolution)?",
    ],
    "clarity": [
        "Is every sentence clear on first read?",
        "Are transitions between scenes and chapters smooth?",
        "Is the POV consistent and clear?",
        "Are there any confusing or ambiguous passages?",
    ],
    "pacing": [
        "Does the story move at the right speed for each section?",
        "Are there slow spots that need tightening?",
        "Are action/tense moments given enough space?",
        "Does the rhythm vary appropriately?",
    ],
    "emotional_depth": [
        "Do key moments land emotionally?",
        "Are character reactions believable and earned?",
        "Is the emotional arc clear and satisfying?",
        "Are there opportunities to deepen reader connection?",
    ],
    "consistency": [
        "Are character details consistent throughout?",
        "Is the timeline and world logic consistent?",
        "Do voice and tone stay consistent?",
        "Are any continuity errors fixed?",
    ],
    "grammar_polish": [
        "Spelling and grammar checked",
        "Repetitive words or phrases reduced",
        "Sentence variety and flow improved",
        "Dialogue punctuation and tags clean",
    ],
    "custom": [],
}
