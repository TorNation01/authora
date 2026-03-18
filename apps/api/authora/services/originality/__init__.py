"""Originality and similarity services."""

from authora.services.originality.ai_origin_risk import (
    RiskResult,
    compute_risk_band,
    run_ai_origin_risk_review,
)
from authora.services.originality.similarity_engine import (
    MatchResult,
    compare_against_corpus,
    compute_overall_similarity,
    extract_plain_text_from_chapters,
)

__all__ = [
    "MatchResult",
    "compare_against_corpus",
    "compute_overall_similarity",
    "extract_plain_text_from_chapters",
    "RiskResult",
    "compute_risk_band",
    "run_ai_origin_risk_review",
]
