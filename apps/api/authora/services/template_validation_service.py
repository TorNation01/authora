"""Template validation service: structure completeness, placeholders, clarity."""

import re
from typing import Any


def _collect_text_values(obj: Any, path: str = "") -> list[tuple[str, str]]:
    """Recursively collect string values from dict/list for placeholder scanning."""
    out: list[tuple[str, str]] = []
    if isinstance(obj, str):
        out.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(_collect_text_values(v, f"{path}.{k}" if path else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(_collect_text_values(v, f"{path}[{i}]"))
    return out


# Placeholder markers that indicate incomplete content
PLACEHOLDER_PATTERNS = [
    r"\bTODO\b",
    r"\bTBD\b",
    r"\bFIXME\b",
    r"\[placeholder\]",
    r"\[insert\s+",
    r"\[xxx\]",
    r"xxx\b",
    r"<placeholder>",
    r"placeholder\s+text",
    r"lorem\s+ipsum",
]


def _has_placeholder_content(text: str) -> bool:
    """Check if text contains placeholder markers."""
    if not text or not isinstance(text, str):
        return False
    lower = text.lower().strip()
    if len(lower) < 3:
        return False
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def _min_meaningful_length(s: str, min_len: int = 20) -> bool:
    """Check if string has meaningful content (not just whitespace/short)."""
    if not s:
        return False
    cleaned = s.strip()
    return len(cleaned) >= min_len


def validate_template_payload(
    payload: dict[str, Any] | None,
    *,
    name: str = "",
    description: str | None = None,
) -> dict[str, Any]:
    """
    Validate template submission payload.
    Returns { "valid": bool, "errors": [...], "warnings": [...], "checks": {...} }.
    """
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool | str] = {}

    payload = payload or {}

    # --- Structure completeness ---
    has_structure = False
    planning = payload.get("default_structure", {}) or {}
    planning_sections = planning.get("planning_sections") if isinstance(planning, dict) else []
    chapter_skeletons = payload.get("chapter_skeletons") or []

    if planning_sections and len(planning_sections) >= 1:
        has_structure = True
    if chapter_skeletons and len(chapter_skeletons) >= 1:
        has_structure = True
    if payload.get("default_milestones") and len(payload.get("default_milestones", [])) >= 1:
        has_structure = True

    checks["structure_complete"] = has_structure
    if not has_structure:
        errors.append(
            "Template must have structure: add default_structure.planning_sections, "
            "chapter_skeletons, or default_milestones."
        )

    # --- No placeholder content ---
    all_text = _collect_text_values(payload)
    if description:
        all_text.append(("description", description))
    if name:
        all_text.append(("name", name))

    placeholder_found: list[str] = []
    for path, text in all_text:
        if _has_placeholder_content(text):
            placeholder_found.append(path)

    checks["no_placeholders"] = len(placeholder_found) == 0
    if placeholder_found:
        errors.append(
            f"Found placeholder content in: {', '.join(placeholder_found[:5])}"
            + (f" (and {len(placeholder_found) - 5} more)" if len(placeholder_found) > 5 else "")
        )

    # --- Clarity of instructions ---
    who_it_is_for = payload.get("who_it_is_for") or ""
    expected_outcome = payload.get("expected_outcome") or ""
    suggested_workflow = payload.get("suggested_workflow") or ""

    who_ok = _min_meaningful_length(str(who_it_is_for), 15)
    outcome_ok = _min_meaningful_length(str(expected_outcome), 15)
    workflow_ok = _min_meaningful_length(str(suggested_workflow), 15)

    checks["who_it_is_for_clear"] = who_ok
    checks["expected_outcome_clear"] = outcome_ok
    checks["suggested_workflow_clear"] = workflow_ok

    if not who_ok:
        warnings.append("who_it_is_for should describe the target audience (15+ chars)")
    if not outcome_ok:
        warnings.append("expected_outcome should describe what users achieve (15+ chars)")
    if not workflow_ok:
        warnings.append("suggested_workflow should describe how to use the template (15+ chars)")

    # --- Description ---
    desc_ok = _min_meaningful_length(description or "", 20)
    checks["description_clear"] = desc_ok
    if not desc_ok:
        warnings.append("description should be at least 20 characters")

    valid = len(errors) == 0
    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }
