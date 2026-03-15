"""In-memory cache for reference lookups - latency-aware fallbacks."""

import time
from collections import OrderedDict
from threading import Lock
from typing import Any, Callable, TypeVar

T = TypeVar("T")

# Default TTL: 24 hours for dictionary/thesaurus (stable data)
CACHE_TTL = 86400
# Max entries per cache
MAX_ENTRIES = 2000


class TTLCache(OrderedDict[str, tuple[Any, float]]):
    """LRU cache with TTL."""

    def __init__(self, ttl: float = CACHE_TTL, max_entries: int = MAX_ENTRIES, *args: Any, **kwargs: Any):
        self.ttl = ttl
        self.max_entries = max_entries
        self.lock = Lock()
        super().__init__(*args, **kwargs)

    def get(self, key: str) -> Any | None:
        with self.lock:
            if key not in self:
                return None
            value, expiry = self[key]
            if time.time() > expiry:
                del self[key]
                return None
            self.move_to_end(key)
            return value

    def set(self, key: str, value: Any) -> None:
        with self.lock:
            if key in self:
                self.move_to_end(key)
            self[key] = (value, time.time() + self.ttl)
            if len(self) > self.max_entries:
                self.popitem(last=False)


# Module-level caches
_dict_cache: TTLCache | None = None
_thesaurus_cache: TTLCache | None = None


def get_dict_cache() -> TTLCache:
    global _dict_cache
    if _dict_cache is None:
        _dict_cache = TTLCache(ttl=CACHE_TTL, max_entries=MAX_ENTRIES)
    return _dict_cache


def get_thesaurus_cache() -> TTLCache:
    global _thesaurus_cache
    if _thesaurus_cache is None:
        _thesaurus_cache = TTLCache(ttl=CACHE_TTL, max_entries=MAX_ENTRIES)
    return _thesaurus_cache


async def cached_lookup(
    cache: TTLCache,
    key: str,
    fetch: Callable[[], Any],
    fallback: Any | None = None,
) -> Any:
    """Get from cache or fetch. On fetch failure, return fallback."""
    cached = cache.get(key)
    if cached is not None:
        return cached
    try:
        result = await fetch()
        if result is not None:
            cache.set(key, result)
        return result
    except Exception:
        return fallback
