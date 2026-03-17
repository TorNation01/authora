"""Story Density Engine."""

from authora.services.density.scanner import run_density_scan
from authora.services.density.fix_assistant import get_density_fix_guidance
from authora.services.density.trim_vs_strengthen_engine import decide_action, get_alternatives_comparison

__all__ = [
    "run_density_scan",
    "get_density_fix_guidance",
    "decide_action",
    "get_alternatives_comparison",
]
