"""AI-powered analysis: grammar, clarity, structure, fiction/nonfiction hints."""

import json
from typing import Any

from authora.infrastructure.ai_provider.factory import get_ai_provider


async def analyze_grammar_clarity(text: str, book_type: str = "fiction") -> dict:
    """AI analysis for grammar and clarity issues."""
    provider = get_ai_provider()
    if not provider or not hasattr(provider, "complete_sync"):
        return {"issues": [], "suggestions": [], "clarity_score": 0, "ai_available": False}

    system = """You are an expert editor. Analyze the text for:
1. Grammar and punctuation issues
2. Clarity problems (unclear phrasing, awkward constructions)
3. Wordiness or redundancy

Respond with a JSON object:
{
  "issues": [{"type": "grammar|clarity|wordiness", "original": "excerpt", "suggestion": "improvement", "severity": "low|medium|high"}],
  "clarity_score": 0-100,
  "summary": "Brief overall assessment"
}
Keep issues to the 5 most important. Use exact text excerpts."""

    prompt = f"Analyze this {book_type} text:\n\n{text[:4000]}"

    try:
        text_out = await provider.complete_sync(prompt, system, max_tokens=1024)
        if "[AI not configured" in str(text_out):
            return {"issues": [], "suggestions": [], "clarity_score": 0, "ai_available": False}
        # Extract JSON from response
        start = text_out.find("{")
        end = text_out.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text_out[start:end])
            data["ai_available"] = True
            return data
    except Exception:
        pass
    return {"issues": [], "suggestions": [], "clarity_score": 0, "ai_available": False}


async def analyze_structure(text: str, chapter_title: str = "") -> dict:
    """AI analysis for structure: opening, ending, flow."""
    provider = get_ai_provider()
    if not provider or not hasattr(provider, "complete_sync"):
        return {"opening_strength": 0, "ending_strength": 0, "suggestions": [], "ai_available": False}

    system = """You are an expert editor. Analyze the chapter structure:
1. Opening: Does it hook the reader? Score 0-100.
2. Ending: Does it satisfy or propel forward? Score 0-100.
3. Flow: Any structural suggestions?

Respond with JSON:
{
  "opening_strength": 0-100,
  "ending_strength": 0-100,
  "opening_hint": "Brief hint to improve opening",
  "ending_hint": "Brief hint to improve ending",
  "suggestions": ["structural suggestion 1", "structural suggestion 2"]
}"""

    prompt = f"Chapter: {chapter_title or 'Untitled'}\n\n{text[:3000]}"

    try:
        text_out = await provider.complete_sync(prompt, system, max_tokens=512)
        start = text_out.find("{")
        end = text_out.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text_out[start:end])
            data["ai_available"] = True
            return data
    except Exception:
        pass
    return {"opening_strength": 0, "ending_strength": 0, "suggestions": [], "ai_available": False}


async def analyze_fiction_hints(text: str) -> dict:
    """Fiction-specific: pacing, dialogue balance, tension."""
    provider = get_ai_provider()
    if not provider or not hasattr(provider, "complete_sync"):
        return {"pacing": "", "dialogue_balance": "", "tension": "", "suggestions": [], "ai_available": False}

    system = """You are an expert fiction editor. Analyze:
1. Pacing: Is the rhythm appropriate? Any slow or rushed sections?
2. Dialogue balance: Good mix of dialogue vs narrative?
3. Tension: Consistency of tension/stakes?

Respond with JSON:
{
  "pacing": "Brief assessment",
  "dialogue_balance": "Brief assessment",
  "tension": "Brief assessment",
  "suggestions": ["hint 1", "hint 2"]
}"""

    prompt = f"Analyze this fiction excerpt:\n\n{text[:3500]}"

    try:
        text_out = await provider.complete_sync(prompt, system, max_tokens=512)
        start = text_out.find("{")
        end = text_out.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text_out[start:end])
            data["ai_available"] = True
            return data
    except Exception:
        pass
    return {"pacing": "", "dialogue_balance": "", "tension": "", "suggestions": [], "ai_available": False}


async def analyze_nonfiction_hints(text: str) -> dict:
    """Nonfiction-specific: clarity, teaching flow, argument strength, actionability."""
    provider = get_ai_provider()
    if not provider or not hasattr(provider, "complete_sync"):
        return {"teaching_flow": "", "argument_strength": "", "actionability": "", "suggestions": [], "ai_available": False}

    system = """You are an expert nonfiction editor. Analyze:
1. Teaching flow: Does the logic build clearly? Easy to follow?
2. Argument strength: Are claims supported? Any weak spots?
3. Actionability: Are takeaways clear and actionable?

Respond with JSON:
{
  "teaching_flow": "Brief assessment",
  "argument_strength": "Brief assessment",
  "actionability": "Brief assessment",
  "suggestions": ["hint 1", "hint 2"]
}"""

    prompt = f"Analyze this nonfiction excerpt:\n\n{text[:3500]}"

    try:
        text_out = await provider.complete_sync(prompt, system, max_tokens=512)
        start = text_out.find("{")
        end = text_out.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text_out[start:end])
            data["ai_available"] = True
            return data
    except Exception:
        pass
    return {"teaching_flow": "", "argument_strength": "", "actionability": "", "suggestions": [], "ai_available": False}
