"""AI safety filters and rate limits."""

import time
from collections import defaultdict
from threading import Lock

from authora.config import get_settings


# Simple in-memory rate limiter (per user)
_rate_cache: dict[str, list[float]] = defaultdict(list)
_rate_lock = Lock()

# Default: 60 requests per minute per user
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW = 60  # seconds


def check_rate_limit(user_id: str) -> bool:
    """Check if user is within rate limit. Returns True if allowed."""
    settings = get_settings()
    if getattr(settings, "ai_rate_limit_per_minute", None) is not None:
        limit = settings.ai_rate_limit_per_minute
    else:
        limit = RATE_LIMIT_REQUESTS

    now = time.time()
    with _rate_lock:
        key = str(user_id)
        window_start = now - RATE_LIMIT_WINDOW
        _rate_cache[key] = [t for t in _rate_cache[key] if t > window_start]
        if len(_rate_cache[key]) >= limit:
            return False
        _rate_cache[key].append(now)
    return True


def get_remaining_requests(user_id: str) -> int:
    """Get remaining requests in current window."""
    settings = get_settings()
    limit = getattr(settings, "ai_rate_limit_per_minute", None) or RATE_LIMIT_REQUESTS
    now = time.time()
    with _rate_lock:
        key = str(user_id)
        window_start = now - RATE_LIMIT_WINDOW
        _rate_cache[key] = [t for t in _rate_cache[key] if t > window_start]
        return max(0, limit - len(_rate_cache[key]))


# Basic content filter - block obviously harmful patterns
BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "disregard your",
    "jailbreak",
    "DAN mode",
]


def filter_prompt(prompt: str) -> tuple[str, bool]:
    """
    Basic prompt safety filter.
    Returns (filtered_prompt, is_safe).
    If not safe, returns truncated/filtered version.
    """
    if not prompt or len(prompt) > 100_000:
        return ("", False)
    lower = prompt.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in lower:
            return (prompt[:500] + "\n[Filtered]", False)
    return (prompt, True)
