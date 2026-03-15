"""Security middleware: rate limiting, secure headers, request ID."""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


# In-memory rate limit store: {key: (count, window_start)}
_rate_limit_store: dict[str, tuple[int, float]] = {}
_rate_limit_cleanup_interval = 60.0  # seconds
_last_cleanup = time.monotonic()


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
    # Group by /api/v1 prefix for API routes
    if path.startswith("/api/"):
        return f"{ip}:api"
    return f"{ip}:{path.split('/')[1] if '/' in path else 'root'}"


def _cleanup_expired_entries():
    """Remove expired rate limit entries."""
    global _last_cleanup
    now = time.monotonic()
    if now - _last_cleanup < _rate_limit_cleanup_interval:
        return
    _last_cleanup = now
    window_sec = 60
    cutoff = now - window_sec
    expired = [k for k, (_, start) in _rate_limit_store.items() if start < cutoff]
    for k in expired:
        del _rate_limit_store[k]


# Default: 100 requests per minute per IP per key
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # seconds

SECURE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}


class SecurityMiddleware(BaseHTTPMiddleware):
    """Add rate limiting, secure headers, and request ID."""

    def __init__(
        self,
        app,
        rate_limit_requests: int = RATE_LIMIT_REQUESTS,
        rate_limit_window: int = RATE_LIMIT_WINDOW,
        skip_paths: set[str] | None = None,
    ):
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.skip_paths = skip_paths or {"/health", "/health/ready", "/"}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Add request ID
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Rate limiting (skip health/docs)
        if request.url.path not in self.skip_paths:
            key = _rate_limit_key(request)
            now = time.monotonic()
            _cleanup_expired_entries()

            if key in _rate_limit_store:
                count, window_start = _rate_limit_store[key]
                if now - window_start >= self.rate_limit_window:
                    _rate_limit_store[key] = (1, now)
                else:
                    count += 1
                    if count > self.rate_limit_requests:
                        return JSONResponse(
                            {"detail": "Rate limit exceeded", "request_id": request_id},
                            status_code=429,
                            headers={
                                "Retry-After": str(self.rate_limit_window),
                                "X-Request-ID": request_id,
                            },
                        )
                    _rate_limit_store[key] = (count, window_start)
            else:
                _rate_limit_store[key] = (1, now)

        response = await call_next(request)

        # Add secure headers
        for name, value in SECURE_HEADERS.items():
            response.headers.setdefault(name, value)
        response.headers["X-Request-ID"] = request_id

        return response
