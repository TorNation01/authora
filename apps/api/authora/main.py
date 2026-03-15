"""AUTHORA API main application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from authora.api.routes import accountability, admin, ai, ai_actions, auth, billing, books, config, content, dictionary, editing, export, fiction, ghostwriter, goals, gamification, journey, leads, nonfiction, notes, projects, reference, setup
from authora.config import get_settings
from authora.middleware.audit import AuditMiddleware
from authora.middleware.security import SecurityMiddleware

settings = get_settings()


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

app.add_middleware(SecurityMiddleware)  # First: rate limit, headers, request ID
app.add_middleware(AuditMiddleware)  # Second: audit log (needs request_id from Security)
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
app.include_router(leads.router, prefix="/api/v1")


@app.get("/health")
async def health():
    """Health check - liveness."""
    return {"status": "ok", "app": settings.app_name}


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
        {"status": "ready" if ready else "degraded", "checks": checks, "app": settings.app_name},
        status_code=status_code,
    )


@app.get("/")
async def root():
    """Root."""
    return {"app": settings.app_name, "docs": "/api/docs"}
