"""AUTHORA API main application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from authora.api.routes import accountability, admin, ai, ai_actions, auth, billing, books, config, content, dictionary, editing, export, fiction, ghostwriter, goals, gamification, journey, leads, nonfiction, notes, projects, rag, reference, setup
from authora.config import get_settings
from authora.middleware.audit import AuditMiddleware
from authora.middleware.integration_forwarding import IntegrationAuditForwardingMiddleware
from authora.middleware.security import SecurityMiddleware

logger = logging.getLogger(__name__)
settings = get_settings()


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


async def _validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """PII-safe validation error response with request ID."""
    errors = exc.errors()
    detail = [{"loc": e["loc"], "msg": e["msg"]} for e in errors]
    return JSONResponse(
        status_code=422,
        content={"detail": detail, "request_id": _request_id(request)},
    )


async def _http_exception_handler(request: Request, exc) -> JSONResponse:
    """HTTPException with request ID in response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "request_id": _request_id(request)},
    )


async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """PII-safe 500 handler: log internal, return generic message."""
    request_id = _request_id(request)
    logger.exception("Unhandled exception request_id=%s path=%s", request_id, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again later.",
            "request_id": request_id,
        },
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI-powered book builder and writing studio API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Exception handlers (PII-safe, request ID in responses)
app.add_exception_handler(RequestValidationError, _validation_exception_handler)
app.add_exception_handler(Exception, _unhandled_exception_handler)
# HTTPException before Exception so HTTP errors get request_id
app.add_exception_handler(HTTPException, _http_exception_handler)

app.add_middleware(SecurityMiddleware)  # First: rate limit, headers, request ID
app.add_middleware(AuditMiddleware)  # Second: audit log (needs request_id from Security)
app.add_middleware(IntegrationAuditForwardingMiddleware)  # Optional: forward to Anakatech when enabled
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(content.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(books.router, prefix="/api/v1")
app.include_router(ghostwriter.router, prefix="/api/v1")
app.include_router(notes.project_router, prefix="/api/v1")
app.include_router(notes.book_router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(ai_actions.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")
app.include_router(dictionary.router, prefix="/api/v1")
app.include_router(reference.router, prefix="/api/v1")
app.include_router(setup.router, prefix="/api/v1")
app.include_router(goals.router, prefix="/api/v1")
app.include_router(accountability.router, prefix="/api/v1")
app.include_router(gamification.router, prefix="/api/v1")
app.include_router(journey.router, prefix="/api/v1")
app.include_router(fiction.router, prefix="/api/v1")
app.include_router(nonfiction.router, prefix="/api/v1")
app.include_router(editing.router, prefix="/api/v1")
app.include_router(rag.router, prefix="/api/v1")
app.include_router(leads.router, prefix="/api/v1")


@app.get("/health")
async def health():
    """Health check - liveness."""
    return {"status": "ok", "app": settings.app_name, "version": "1.0.0"}


@app.get("/health/ready")
async def health_ready():
    """Readiness - checks DB and Redis connectivity."""
    from sqlalchemy import text
    from authora.database import async_session_factory

    checks = {"database": False, "redis": False}
    try:
        async with async_session_factory() as db:
            await db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        logger.exception("Readiness check: database failed")
    try:
        from redis.asyncio import Redis
        from authora.config import get_settings

        r = Redis.from_url(get_settings().redis_url)
        await r.ping()
        await r.aclose()
        checks["redis"] = True
    except Exception:
        logger.exception("Readiness check: redis failed")

    ready = all(checks.values())
    status_code = 200 if ready else 503
    return JSONResponse(
        {"status": "ready" if ready else "degraded", "checks": checks, "app": settings.app_name, "version": "1.0.0"},
        status_code=status_code,
    )


@app.get("/")
async def root():
    """Root."""
    return {"app": settings.app_name, "docs": "/api/docs"}
