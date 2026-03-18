"""AUTHORA API main application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from authora.api.routes import accountability, admin, affiliates, ai, ai_actions, auth, billing, books, collaboration, community, config, content, content_annotations, creators, density, dictionary, editing, export, fiction, frameworks, ghostwriter, goals, gamification, growth, integrity, journey, leads, nonfiction, notes, organizations, projects, rag, reference, revision_passes, setup, templates, vault
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
    """Application lifespan. Validates AI dependencies at startup."""
    from authora.services.ai_config import (  # noqa: E402
        get_available_providers,
        get_environment,
        is_ai_available,
        log_provider_status,
        validate_ollama_config,
        validate_openai_config,
        validate_anthropic_config,
    )

    env = get_environment()
    logger.info("AUTHORA starting in %s environment", env)

    # Error tracking (optional)
    if settings.sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration

            sentry_sdk.init(
                dsn=settings.sentry_dsn,
                environment=env,
                integrations=[FastApiIntegration()],
                traces_sample_rate=0.1,
                send_default_pii=False,
            )
            logger.info("Sentry error tracking enabled")
        except ImportError:
            logger.warning("SENTRY_DSN set but sentry-sdk not installed. pip install sentry-sdk.")

    providers = get_available_providers()
    for name, configured in providers.items():
        log_provider_status(name, configured)

    if not is_ai_available():
        logger.warning(
            "No AI providers configured. AI features will be unavailable. "
            "Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or OLLAMA_ENABLED=true."
        )
    else:
        validations = [
            validate_openai_config(),
            validate_anthropic_config(),
            validate_ollama_config(),
        ]
        if any(ok for ok, _ in validations):
            logger.info("AI providers ready. Graceful fallback enabled if some unavailable.")
        else:
            logger.warning("AI config present but validation failed. Check keys and OLLAMA_BASE_URL.")

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

app.add_middleware(
    SecurityMiddleware,
    rate_limit_requests=settings.rate_limit_requests_per_minute or 100,
    rate_limit_auth_attempts=settings.rate_limit_auth_attempts or 5,
    rate_limit_auth_window=settings.rate_limit_auth_window_seconds,
    hsts_max_age=settings.hsts_max_age,
)  # First: rate limit, headers, request ID
app.add_middleware(GZipMiddleware, minimum_size=500)  # Compress responses > 500 bytes
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
app.include_router(organizations.router, prefix="/api/v1")
app.include_router(growth.router, prefix="/api/v1")
app.include_router(affiliates.router, prefix="/api/v1")
app.include_router(creators.router, prefix="/api/v1")
app.include_router(community.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(content.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(templates.router, prefix="/api/v1")
app.include_router(frameworks.router, prefix="/api/v1")
app.include_router(books.router, prefix="/api/v1")
app.include_router(content_annotations.router, prefix="/api/v1")
app.include_router(revision_passes.router, prefix="/api/v1")
app.include_router(collaboration.router, prefix="/api/v1")
app.include_router(collaboration.invite_router, prefix="/api/v1")
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
app.include_router(integrity.router, prefix="/api/v1")
app.include_router(density.router, prefix="/api/v1")
app.include_router(rag.router, prefix="/api/v1")
app.include_router(leads.router, prefix="/api/v1")
app.include_router(vault.router, prefix="/api/v1")


@app.get("/health")
async def health():
    """Health check - liveness."""
    return {"status": "ok", "app": settings.app_name, "version": "1.0.0"}


@app.get("/health/ai")
async def health_ai():
    """AI providers availability (for load balancers, no auth). Returns minimal status."""
    from authora.services.ai_config import get_available_providers, is_ai_available

    providers = get_available_providers()
    available = is_ai_available()
    return {
        "ai_available": available,
        "providers_configured": list(k for k, v in providers.items() if v),
        "status": "ok" if available else "degraded",
    }


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
