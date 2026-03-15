"""Optional integration forwarding middleware.

Forwards request-level audit events to Anakatech when shared analytics
is enabled. No-op when integration is disabled.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from authora.integration.analytics import forward_audit_event, should_forward_audit_events


class IntegrationAuditForwardingMiddleware(BaseHTTPMiddleware):
    """Forwards request audit events to Anakatech when enabled."""

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
        response = await call_next(request)

        if not should_forward_audit_events():
            return response

        if request.url.path in self.exclude_paths:
            return response

        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = str(getattr(request.state.user, "id", ""))
        client_ip = request.client.host if request.client else None

        # Fire-and-forget; do not block response
        await forward_audit_event(
            action="request",
            resource=request.url.path,
            resource_id=None,
            user_id=user_id,
            details={"method": request.method, "status_code": response.status_code},
            ip_address=client_ip,
        )

        return response
