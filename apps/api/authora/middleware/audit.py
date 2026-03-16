"""Audit log middleware - logs request/response for audit trail.
Structlog: first arg is event, do not duplicate in kwargs."""

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger()


class AuditMiddleware(BaseHTTPMiddleware):
    """Log API requests for audit trail."""

    def __init__(self, app, exclude_paths: set[str] | None = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or {
            "/health",
            "/health/ready",
            "/",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        request_id = getattr(request.state, "request_id", None)
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        response = await call_next(request)

        # Log after response - avoid logging sensitive paths in detail
        # Ecosystem convention: app, request_id, event for log aggregation
        log_data = {
            "app": "authora",
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": response.status_code,
            "client_ip": client_ip,
        }
        logger.info("audit_request", **log_data)

        return response
