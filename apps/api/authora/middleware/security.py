"""Security middleware: rate limiting, secure headers, request ID."""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# In-memory rate limit store (fallback when Redis unavailable): {key: (count, window_start)}
_rate_limit_store: dict[str, tuple[int, float]] = {}
_rate_limit_cleanup_interval = 60.0  # seconds
_last_cleanup = time.monotonic()
_redis_available: bool | None = None


def _get_client_ip(request: Request) -> str:
    """Get client IP, considering X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


def _rate_limit_key(request: Request) -> str:
    """Key for rate limiting: IP + path prefix."""
    ip = _get_client_ip(request)
    path = request.url.path
    # Stricter key for auth endpoints (login/register brute-force protection)
    if "/auth/login" in path or "/auth/register" in path:
        return f"auth:{ip}"
    # Group by /api/v1 prefix for API routes
    if path.startswith("/api/"):
        return f"{ip}:api"
    return f"{ip}:{path.split('/')[1] if '/' in path else 'root'}"


def _is_auth_path(path: str) -> bool:
    """True for login/register (stricter rate limit)."""
    return "/auth/login" in path or "/auth/register" in path


def _cleanup_expired_entries():
    """Remove expired rate limit entries. Uses max window (auth=900s) for cutoff."""
    global _last_cleanup
    now = time.monotonic()
    if now - _last_cleanup < _rate_limit_cleanup_interval:
        return
    _last_cleanup = now
    window_sec = max(RATE_LIMIT_WINDOW, RATE_LIMIT_AUTH_WINDOW)
    cutoff = now - window_sec
    expired = [k for k, (_, start) in _rate_limit_store.items() if start < cutoff]
    for k in expired:
        del _rate_limit_store[k]


# Defaults: 100 req/min general; 5/15min for auth
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_AUTH_ATTEMPTS = 5
RATE_LIMIT_AUTH_WINDOW = 900  # 15 min


async def _check_rate_limit_redis(key: str, limit: int, window: int) -> tuple[bool, bool]:
    """Check rate limit via Redis. Returns (allowed, used_redis). When used_redis=False, caller uses in-memory."""
    global _redis_available
    try:
        from redis.asyncio import Redis

        from authora.config import get_settings

        r = Redis.from_url(get_settings().redis_url, decode_responses=True)
        redis_key = f"ratelimit:{key}"
        count = await r.incr(redis_key)
        if count == 1:
            await r.expire(redis_key, window)
        ttl = await r.ttl(redis_key)
        if ttl < 0:
            await r.expire(redis_key, window)
        await r.aclose()
        _redis_available = True
        return (count <= limit, True)
    except Exception:
        _redis_available = False
        return (True, False)  # Fall back to in-memory


def _secure_headers(hsts_max_age: int | None = None) -> dict[str, str]:
    """Secure headers. HSTS added when hsts_max_age set (HTTPS)."""
    h = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }
    if hsts_max_age:
        h["Strict-Transport-Security"] = f"max-age={hsts_max_age}; includeSubDomains; preload"
    return h


class SecurityMiddleware(BaseHTTPMiddleware):
    """Add rate limiting, secure headers, and request ID."""

    def __init__(
        self,
        app,
        rate_limit_requests: int = RATE_LIMIT_REQUESTS,
        rate_limit_window: int = RATE_LIMIT_WINDOW,
        rate_limit_auth_attempts: int = RATE_LIMIT_AUTH_ATTEMPTS,
        rate_limit_auth_window: int = RATE_LIMIT_AUTH_WINDOW,
        hsts_max_age: int | None = None,
        skip_paths: set[str] | None = None,
    ):
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.rate_limit_auth_attempts = rate_limit_auth_attempts
        self.rate_limit_auth_window = rate_limit_auth_window
        self.hsts_max_age = hsts_max_age
        self.skip_paths = skip_paths or {"/health", "/health/ready", "/health/ai", "/", "/api/docs", "/api/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Add request ID
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Rate limiting (skip health/docs)
        if request.url.path not in self.skip_paths:
            key = _rate_limit_key(request)
            now = time.monotonic()
            limit = self.rate_limit_auth_attempts if _is_auth_path(request.url.path) else self.rate_limit_requests
            window = self.rate_limit_auth_window if _is_auth_path(request.url.path) else self.rate_limit_window

            # Try Redis first (scales across instances)
            allowed, used_redis = await _check_rate_limit_redis(key, limit, window)
            if used_redis:
                if not allowed:
                    return JSONResponse(
                        {"detail": "Rate limit exceeded", "request_id": request_id},
                        status_code=429,
                        headers={
                            "Retry-After": str(window),
                            "X-Request-ID": request_id,
                        },
                    )
            else:
                # Fallback: in-memory when Redis unavailable
                _cleanup_expired_entries()
                if key in _rate_limit_store:
                    count, window_start = _rate_limit_store[key]
                    if now - window_start >= window:
                        _rate_limit_store[key] = (1, now)
                    else:
                        count += 1
                        if count > limit:
                            return JSONResponse(
                                {"detail": "Rate limit exceeded", "request_id": request_id},
                                status_code=429,
                                headers={
                                    "Retry-After": str(window),
                                    "X-Request-ID": request_id,
                                },
                            )
                        _rate_limit_store[key] = (count, window_start)
                else:
                    _rate_limit_store[key] = (1, now)

        response = await call_next(request)

        # Add secure headers (incl. HSTS when configured)
        for name, value in _secure_headers(self.hsts_max_age).items():
            response.headers.setdefault(name, value)
        response.headers["X-Request-ID"] = request_id

        return response
