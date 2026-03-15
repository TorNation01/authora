"""Grammar review integration layer.

Supports pluggable backends: AI (default), LanguageTool API, or custom.
"""

from typing import Any


async def check_grammar(text: str, backend: str = "ai") -> list[dict[str, Any]]:
    """
    Check grammar and return list of issues.
    Each issue: {type, message, offset, length, replacement, context}
    """
    if backend == "ai":
        from authora.services.editing.ai_analysis import analyze_grammar_clarity
        result = await analyze_grammar_clarity(text)
        issues = result.get("issues", [])
        return [
            {
                "type": i.get("type", "grammar"),
                "message": i.get("suggestion", ""),
                "replacement": i.get("suggestion"),
                "context": i.get("original", ""),
                "severity": i.get("severity", "medium"),
            }
            for i in issues
        ]
    # Future: LanguageTool API, etc.
    return []
