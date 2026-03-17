"""Retention service: daily prompts, streak nudges, progress summaries.

Supports the retention system with motivating, non-annoying content.
"""

from datetime import date
from typing import Any

from authora.content.templates import get_all_templates

# Generic prompts when no project-specific context; motivating, not prescriptive
GENERIC_DAILY_PROMPTS: list[str] = [
    "Write the scene you've been avoiding. What makes it hard? Start there.",
    "What does your protagonist want right now? Write them taking one step toward it.",
    "Add a detail that changes how we see a character. One sentence. Then expand.",
    "Write the moment something goes wrong. How does your character respond?",
    "Describe a place through one character's eyes. What do they notice that others wouldn't?",
    "Write a conversation where both people are hiding something.",
    "What's the one thing your character would never say? Have them say it.",
    "Write the transition between two scenes. What's left unsaid?",
    "Start with a question. Let the scene answer it.",
    "Write the aftermath of a big moment. What's different now?",
    "Your character receives unexpected news. How do they react?",
    "Write a scene that could happen in five minutes. Keep the stakes high.",
    "What would your antagonist say to your protagonist right now? Write that exchange.",
    "Describe a ritual—daily, rare, or secret. What does it reveal?",
    "Write the moment before something important. Build the tension.",
    "Your character has to make a choice. Show us the moment of decision.",
    "Write a scene where someone is lying. Don't say they're lying.",
    "What's the weather? Use it to reflect the mood.",
    "Write the first line of a chapter. Then write the second.",
    "Someone enters a room. What do they notice first?",
]


def get_daily_prompt(for_date: date | None = None, project_template_id: str | None = None) -> dict[str, Any]:
    """Return a date-seeded daily writing prompt. Same date = same prompt for all users.

    Args:
        for_date: Date to seed the prompt. Defaults to today (UTC).
        project_template_id: Optional template ID (e.g. romance, thriller) to prefer
            prompts from that template. Falls back to generic if not found.

    Returns:
        {"prompt": str, "date": str, "source": "template" | "generic"}
    """
    d = for_date or date.today()
    date_str = d.isoformat()
    seed = hash(date_str) & 0x7FFFFFFF  # Non-negative int for indexing

    prompts: list[str] = []

    if project_template_id:
        templates = get_all_templates()
        for t in templates:
            if t.get("id") == project_template_id and "writing_prompts" in t:
                prompts.extend(t["writing_prompts"])
        if not prompts and project_template_id:
            for t in templates:
                if "writing_prompts" in t:
                    prompts.extend(t["writing_prompts"])

    if not prompts:
        for t in get_all_templates():
            if "writing_prompts" in t:
                prompts.extend(t["writing_prompts"])

    template_count = len(prompts)
    if not prompts:
        prompts = list(GENERIC_DAILY_PROMPTS)
        template_count = 0
    else:
        prompts = list(prompts) + GENERIC_DAILY_PROMPTS

    idx = seed % len(prompts)
    chosen = prompts[idx]
    source = "template" if idx < template_count else "generic"

    return {
        "prompt": chosen,
        "date": date_str,
        "source": source,
    }
