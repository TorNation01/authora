"""AI-origin risk review: probabilistic, review-aid only.

This is NOT a detector. Does not claim perfect AI detection.
Results are review aids. Human review is central.
"""

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import AIActionLog, Chapter


@dataclass
class RiskResult:
    risk_band: str
    confidence_low: float
    confidence_high: float
    signals_summary: dict[str, Any]
    disclaimer: str


RISK_BANDS = ("low", "medium", "high")


def _compute_signals(chapters: list[dict], ai_action_count: int) -> dict[str, Any]:
    """Compute signals from content_source and AI actions. No certainty."""
    ai_generated = 0
    ai_assisted = 0
    user_written = 0
    total = len(chapters) or 1
    for ch in chapters:
        cs = ch.get("content_source") or ""
        if cs == "ai_generated":
            ai_generated += 1
        elif cs == "ai_assisted":
            ai_assisted += 1
        else:
            user_written += 1
    return {
        "ai_generated_pct": round((ai_generated / total) * 100, 1),
        "ai_assisted_pct": round((ai_assisted / total) * 100, 1),
        "user_written_pct": round((user_written / total) * 100, 1),
        "ai_action_count": ai_action_count,
        "chapter_count": total,
    }


def compute_risk_band(signals: dict[str, Any]) -> RiskResult:
    """
    Compute risk band from signals. Probabilistic only.
    Never presents as sole proof of misconduct.
    """
    ai_gen = signals.get("ai_generated_pct", 0) or 0
    ai_ass = signals.get("ai_assisted_pct", 0) or 0
    ai_actions = signals.get("ai_action_count", 0) or 0
    combined = ai_gen * 1.5 + ai_ass * 0.5 + min(ai_actions * 2, 50)
    if combined >= 80:
        band = "high"
        low, high = 0.6, 0.9
    elif combined >= 40:
        band = "medium"
        low, high = 0.6, 0.85
    else:
        band = "low"
        low, high = 0.5, 0.75
    return RiskResult(
        risk_band=band,
        confidence_low=low,
        confidence_high=high,
        signals_summary=signals,
        disclaimer="This is a review aid only. It does not constitute proof of misconduct. "
        "Human review is required. Results have inherent uncertainty.",
    )


async def run_ai_origin_risk_review(
    db: AsyncSession,
    project_id: str,
    book_id: str,
    chapters: list[dict],
) -> RiskResult:
    """Run AI-origin risk review. Returns probabilistic result."""
    from uuid import UUID

    uid = UUID(project_id) if isinstance(project_id, str) else project_id
    bid = UUID(book_id) if isinstance(book_id, str) else book_id
    r = await db.execute(
        select(AIActionLog).where(
            AIActionLog.project_id == uid,
            AIActionLog.book_id == bid,
        )
    )
    ai_actions = r.scalars().all()
    signals = _compute_signals(chapters, len(ai_actions))
    return compute_risk_band(signals)
