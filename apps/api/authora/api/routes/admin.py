"""Admin/operator control layer - user management, feature flags, monitoring, etc."""

import uuid
from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import AdminUser, CurrentUser, get_db
from authora.config import get_settings
from authora.models import (
    AuditLog,
    Book,
    Chapter,
    ExportJob,
    FeatureFlag,
    NotificationDeliveryLog,
    Plan,
    Project,
    ProjectTemplate,
    Reminder,
    Setting,
    SetupState,
    UsageRecord,
    User,
    WritingFramework,
)
from authora.content.messages import (
    CELEBRATION_MESSAGES,
    ENCOURAGEMENT_MESSAGES,
    RECOVERY_NUDGES,
)
from authora.content.templates import TEMPLATE_IDS

router = APIRouter(prefix="/admin", tags=["admin"])


# --- User management ---


@router.get("/users")
async def admin_list_users(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
):
    """List users with pagination and optional search."""
    q = select(User)
    if search:
        pattern = f"%{search}%"
        q = q.where(or_(User.email.ilike(pattern), func.coalesce(User.display_name, "").ilike(pattern)))
    q = q.order_by(User.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    users = result.scalars().all()
    count_q = select(func.count(User.id))
    if search:
        pattern = f"%{search}%"
        count_q = count_q.where(or_(User.email.ilike(pattern), func.coalesce(User.display_name, "").ilike(pattern)))
    count_result = await db.execute(count_q)
    total = count_result.scalar() or 0
    plan_ids = [u.plan_override_id for u in users if u.plan_override_id]
    plan_map = {}
    if plan_ids:
        plans_result = await db.execute(select(Plan).where(Plan.id.in_(plan_ids)))
        plan_map = {p.id: p.slug for p in plans_result.scalars().all()}
    user_plan_slugs = {str(u.id): plan_map.get(u.plan_override_id) if u.plan_override_id else None for u in users}

    return {
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "display_name": u.display_name,
                "is_active": u.is_active,
                "is_admin": u.is_admin,
                "billing_exempt": u.billing_exempt,
                "plan_override_slug": user_plan_slugs.get(str(u.id)),
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "total": total,
    }


class UserUpdateAdmin(BaseModel):
    is_active: bool | None = None
    is_admin: bool | None = None
    billing_exempt: bool | None = None
    plan_override_slug: str | None = None


@router.patch("/users/{user_id}")
async def admin_update_user(
    user_id: uuid.UUID,
    data: UserUpdateAdmin,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update user (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.is_admin is not None:
        user.is_admin = data.is_admin
    if data.billing_exempt is not None:
        user.billing_exempt = data.billing_exempt
    if data.plan_override_slug is not None:
        if data.plan_override_slug == "":
            user.plan_override_id = None
        else:
            r2 = await db.execute(select(Plan).where(Plan.slug == data.plan_override_slug))
            plan = r2.scalar_one_or_none()
            if not plan:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
            user.plan_override_id = plan.id
    await db.flush()
    await db.refresh(user)
    plan_slug = None
    if user.plan_override_id:
        p = await db.get(Plan, user.plan_override_id)
        plan_slug = p.slug if p else None
    return {
        "id": str(user.id),
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "billing_exempt": user.billing_exempt,
        "plan_override_slug": plan_slug,
    }


# --- Feature flags ---


@router.get("/feature-flags")
async def admin_list_feature_flags(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List feature flags (DB + env)."""
    result = await db.execute(select(FeatureFlag).order_by(FeatureFlag.key))
    flags = result.scalars().all()
    env_flags = get_settings().get_feature_flags()
    return {
        "db_flags": [{"key": f.key, "enabled": f.enabled, "rules": f.rules} for f in flags],
        "env_flags": env_flags,
    }


class FeatureFlagUpdate(BaseModel):
    enabled: bool
    rules: dict[str, Any] | None = None


@router.put("/feature-flags/{key}")
async def admin_update_feature_flag(
    key: str,
    data: FeatureFlagUpdate,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update feature flag in DB (settings table used by FeatureFlagService)."""
    setting_key = f"feature.{key}"
    result = await db.execute(select(Setting).where(Setting.key == setting_key))
    row = result.scalar_one_or_none()
    if not row:
        row = Setting(key=setting_key, value={"enabled": data.enabled, "rules": data.rules or {}})
        db.add(row)
    else:
        row.value = {**(row.value or {}), "enabled": data.enabled, "rules": data.rules or {}}
    await db.flush()
    return {"key": key, "enabled": data.enabled}


# --- AI usage visibility ---


@router.get("/ai-usage")
async def admin_ai_usage(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    period: str = Query("2025-03", description="YYYY-MM"),
    metric: str | None = Query(None, description="ai_actions, exports, etc."),
):
    """Aggregate AI/usage metrics by user and period."""
    q = select(UsageRecord.user_id, UsageRecord.metric, func.sum(UsageRecord.value).label("total")).where(
        UsageRecord.period == period
    ).group_by(UsageRecord.user_id, UsageRecord.metric)
    if metric:
        q = q.where(UsageRecord.metric == metric)
    result = await db.execute(q)
    rows = result.all()
    by_user: dict[str, dict[str, int]] = {}
    for user_id, m, total in rows:
        uid = str(user_id)
        if uid not in by_user:
            by_user[uid] = {}
        by_user[uid][m] = total
    return {"period": period, "by_user": by_user, "rows": [{"user_id": str(r[0]), "metric": r[1], "total": r[2]} for r in rows]}


# --- Export job monitoring ---


@router.get("/export-jobs")
async def admin_export_jobs(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: str | None = Query(None, description="pending|processing|completed|failed"),
    limit: int = Query(50, ge=1, le=200),
):
    """List export jobs with status."""
    q = select(ExportJob).order_by(ExportJob.created_at.desc()).limit(limit)
    if status_filter:
        q = q.where(ExportJob.status == status_filter)
    result = await db.execute(q)
    jobs = result.scalars().all()
    return {
        "jobs": [
            {
                "id": str(j.id),
                "user_id": str(j.user_id),
                "book_id": str(j.book_id),
                "format": j.format,
                "status": j.status,
                "error_message": j.error_message,
                "created_at": j.created_at.isoformat() if j.created_at else None,
                "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            }
            for j in jobs
        ],
    }


# --- Reminder monitoring ---


@router.get("/reminders")
async def admin_reminders(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    active_only: bool = Query(True),
):
    """List reminders across users."""
    q = select(Reminder).join(User).order_by(Reminder.created_at.desc())
    if active_only:
        q = q.where(Reminder.is_active == True)
    result = await db.execute(q)
    reminders = result.scalars().all()
    return {
        "reminders": [
            {
                "id": str(r.id),
                "user_id": str(r.user_id),
                "reminder_type": r.reminder_type,
                "scheduled_time": r.scheduled_time,
                "is_active": r.is_active,
                "last_triggered_at": r.last_triggered_at.isoformat() if r.last_triggered_at else None,
            }
            for r in reminders
        ],
    }


# --- Error monitoring (placeholder - no persisted error log) ---


@router.get("/errors")
async def admin_errors(
    current_user: AdminUser,
):
    """Error monitoring. Returns empty list; integrate Sentry/Loki for persisted errors."""
    return {
        "errors": [],
        "total": 0,
        "message": "No persisted errors. Integrate SENTRY_DSN or log aggregation for error monitoring.",
        "suggestions": [
            "Add SENTRY_DSN for Sentry integration",
            "Ship logs to Loki/Elasticsearch for querying",
        ],
    }


# --- System health ---


@router.get("/health/detailed")
async def admin_health_detailed(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Detailed system health (DB, Redis, config)."""
    from sqlalchemy import text

    checks: dict[str, Any] = {"database": False, "redis": False}
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        checks["database_error"] = str(e)
    try:
        from redis.asyncio import Redis
        r = Redis.from_url(get_settings().redis_url)
        await r.ping()
        await r.aclose()
        checks["redis"] = True
    except Exception as e:
        checks["redis_error"] = str(e)

    s = get_settings()
    ai_configured = bool(
        getattr(s, "openai_api_key", None)
        or getattr(s, "anthropic_api_key", None)
        or getattr(s, "ollama_enabled", False)
    )
    return {
        "status": "ok" if checks["database"] else "degraded",
        "checks": checks,
        "config": {
            "deployment_mode": s.deployment_mode,
            "storage_provider": s.storage_provider,
            "ai_provider": s.ai_provider,
            "ai_configured": ai_configured,
            "feature_billing": getattr(s, "feature_billing", False),
            "notification_provider": getattr(s, "notification_email_provider", "none"),
        },
    }


# --- Setup state visibility ---


@router.get("/setup-state")
async def admin_setup_state(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """View setup wizard state."""
    result = await db.execute(select(SetupState).order_by(SetupState.key))
    rows = result.scalars().all()
    return {
        "state": {r.key: r.value for r in rows},
    }


# --- Storage usage visibility ---


@router.get("/storage")
async def admin_storage(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Estimate storage usage from DB (books, chapters, notes)."""
    import json

    from sqlalchemy.orm import selectinload

    from authora.models import Note

    books_result = await db.execute(select(func.count(Book.id)))
    books_count = books_result.scalar() or 0
    chapters_result = await db.execute(select(Chapter).options(selectinload(Chapter.book)))
    chapters = chapters_result.scalars().all()
    chapters_count = len(chapters)
    total_content_bytes = 0
    for c in chapters:
        if c.content:
            total_content_bytes += len(json.dumps(c.content).encode())
    notes_result = await db.execute(select(Note))
    for n in notes_result.scalars().all():
        if n.content:
            total_content_bytes += len(str(n.content).encode())
    return {
        "books_count": books_count,
        "chapters_count": chapters_count,
        "estimated_content_bytes_approx": total_content_bytes,
        "estimated_content_mb": round(total_content_bytes / (1024 * 1024), 2),
        "storage_provider": get_settings().storage_provider,
        "note": "Local file storage size not computed. Use du for storage_local_path.",
    }


# --- Audit logs ---


@router.get("/audit-logs")
async def admin_audit_logs(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: uuid.UUID | None = Query(None),
    resource: str | None = Query(None),
    action: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    """List audit logs with filters."""
    q = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if user_id:
        q = q.where(AuditLog.user_id == user_id)
    if resource:
        q = q.where(AuditLog.resource == resource)
    if action:
        q = q.where(AuditLog.action == action)
    result = await db.execute(q)
    logs = result.scalars().all()
    return {
        "logs": [
            {
                "id": str(l.id),
                "user_id": str(l.user_id) if l.user_id else None,
                "action": l.action,
                "resource": l.resource,
                "resource_id": l.resource_id,
                "ip_address": l.ip_address,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in logs
        ],
    }


# --- Operational alerts ---


@router.get("/alerts")
async def admin_operational_alerts(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Aggregate operational alerts: failed jobs, failed notifications."""
    failed_exports = (
        await db.execute(
            select(func.count(ExportJob.id)).where(ExportJob.status == "failed")
        )
    ).scalar() or 0
    failed_notifications = (
        await db.execute(
            select(func.count(NotificationDeliveryLog.id)).where(
                NotificationDeliveryLog.status == "failed"
            )
        )
    ).scalar() or 0
    return {
        "failed_export_jobs": failed_exports,
        "failed_notification_deliveries": failed_notifications,
        "has_alerts": failed_exports > 0 or failed_notifications > 0,
    }


# --- Notification delivery monitoring ---


@router.get("/notification-logs")
async def admin_notification_logs(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: str | None = Query(None, description="sent|failed|pending"),
    limit: int = Query(50, ge=1, le=200),
):
    """List notification delivery logs."""
    q = (
        select(NotificationDeliveryLog)
        .order_by(NotificationDeliveryLog.created_at.desc())
        .limit(limit)
    )
    if status_filter:
        q = q.where(NotificationDeliveryLog.status == status_filter)
    result = await db.execute(q)
    logs = result.scalars().all()
    return {
        "logs": [
            {
                "id": str(l.id),
                "user_id": str(l.user_id),
                "notification_type": l.notification_type,
                "channel": l.channel,
                "status": l.status,
                "error_message": l.error_message,
                "retry_count": l.retry_count,
                "created_at": l.created_at.isoformat() if l.created_at else None,
                "sent_at": l.sent_at.isoformat() if l.sent_at else None,
            }
            for l in logs
        ],
    }


# --- Support tools ---


@router.get("/support/notes/{user_id}")
async def admin_get_support_notes(
    user_id: uuid.UUID,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get support notes for a user."""
    key = f"support_notes.{user_id}"
    result = await db.execute(select(Setting).where(Setting.key == key))
    row = result.scalar_one_or_none()
    return {"notes": (row.value or {}).get("notes", "") if row and row.value else ""}


class SupportNotesUpdate(BaseModel):
    notes: str


@router.put("/support/notes/{user_id}")
async def admin_update_support_notes(
    user_id: uuid.UUID,
    data: SupportNotesUpdate,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update support notes for a user."""
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    key = f"support_notes.{user_id}"
    result = await db.execute(select(Setting).where(Setting.key == key))
    row = result.scalar_one_or_none()
    value = {"notes": data.notes, "updated_by": str(current_user.id)}
    if not row:
        row = Setting(key=key, value=value)
        db.add(row)
    else:
        row.value = value
    await db.flush()
    return {"ok": True}


@router.get("/support/user-context/{user_id}")
async def admin_user_context(
    user_id: uuid.UUID,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get user context for support (projects, books, recent activity)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    projects_result = await db.execute(select(Project).where(Project.user_id == user_id))
    projects = projects_result.scalars().all()
    books_result = await db.execute(
        select(Book).join(Project).where(Project.user_id == user_id)
    )
    books = books_result.scalars().all()
    return {
        "user": {"id": str(user.id), "email": user.email, "display_name": user.display_name, "is_active": user.is_active},
        "projects_count": len(projects),
        "books_count": len(books),
    }


# --- Content template management ---


@router.get("/content-templates")
async def admin_content_templates(
    current_user: AdminUser,
):
    """List content template IDs. Full templates in content/templates.py."""
    return {"template_ids": TEMPLATE_IDS}


# --- Encouragement message management ---


@router.get("/encouragement-messages")
async def admin_encouragement_messages(
    current_user: AdminUser,
):
    """List encouragement, recovery, and celebration message categories."""
    return {
        "encouragement": ENCOURAGEMENT_MESSAGES,
        "recovery_nudges": RECOVERY_NUDGES,
        "celebration": {k: v for k, v in CELEBRATION_MESSAGES.items()},
    }


# --- Accountability rule visibility ---


@router.get("/accountability-rules")
async def admin_accountability_rules(
    current_user: AdminUser,
):
    """List accountability styles and rule constants (read-only)."""
    from authora.models.accountability import (
        ACCOUNTABILITY_STYLES,
        PLAN_STATUSES,
        RECOVERY_PLAN_TYPES,
    )

    return {
        "accountability_styles": ACCOUNTABILITY_STYLES,
        "plan_statuses": PLAN_STATUSES,
        "recovery_plan_types": RECOVERY_PLAN_TYPES,
    }


# --- Gamification rule controls ---


@router.get("/gamification")
async def admin_gamification(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List badge definitions and gamification config."""
    from authora.models import BadgeDefinition

    result = await db.execute(select(BadgeDefinition).order_by(BadgeDefinition.sort_order))
    badges = result.scalars().all()
    return {
        "badges": [
            {
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "category": b.category,
                "xp_reward": b.xp_reward,
                "criteria_type": b.criteria_type,
            }
            for b in badges
        ],
    }


# --- AI provider admin ---


class AdminAIConfigUpdate(BaseModel):
    """Update AI provider configuration (writes to .env)."""

    ai_provider_mode: str | None = Field(None, description="auto | cloud | local")
    ai_provider: str | None = Field(None, description="openai | anthropic | ollama (legacy)")
    ai_model: str | None = Field(None, description="Default model for cloud providers")
    openai_api_key: str | None = Field(None, description="OpenAI API key (empty = leave unchanged)")
    anthropic_api_key: str | None = Field(None, description="Anthropic API key (empty = leave unchanged)")
    ollama_enabled: bool | None = Field(None)
    ollama_base_url: str | None = Field(None)
    ollama_hardware_tier: str | None = Field(None, description="1 | 2 | 3 | 4")


@router.get("/ai/providers")
async def admin_ai_providers(current_user: AdminUser):
    """List AI providers with status."""
    from authora.services.ai_registry import list_available_providers

    s = get_settings()
    providers = list_available_providers()
    return {
        "providers": providers,
        "provider_mode": s.ai_provider_mode,
        "ollama_enabled": s.ollama_enabled,
        "ollama_base_url": s.ollama_base_url if s.ollama_enabled else None,
        "ollama_hardware_tier": getattr(s, "ollama_hardware_tier", None),
        "ai_provider": s.ai_provider,
        "ai_model": s.ai_model,
        "openai_configured": bool(s.openai_api_key),
        "anthropic_configured": bool(s.anthropic_api_key),
    }


@router.put("/ai/config")
async def admin_update_ai_config(data: AdminAIConfigUpdate, current_user: AdminUser):
    """Update AI provider configuration. Writes to .env. Restart API for changes to take effect."""
    from authora.services.setup_wizard import write_env

    updates: dict[str, str] = {}
    if data.ai_provider_mode is not None:
        updates["AI_PROVIDER_MODE"] = data.ai_provider_mode
    if data.ai_provider is not None:
        updates["AI_PROVIDER"] = data.ai_provider
    if data.ai_model is not None:
        updates["AI_MODEL"] = data.ai_model
    if data.openai_api_key:
        updates["OPENAI_API_KEY"] = data.openai_api_key
    if data.anthropic_api_key:
        updates["ANTHROPIC_API_KEY"] = data.anthropic_api_key
    if data.ollama_enabled is not None:
        updates["OLLAMA_ENABLED"] = str(data.ollama_enabled).lower()
    if data.ollama_base_url is not None:
        updates["OLLAMA_BASE_URL"] = data.ollama_base_url
    if data.ollama_hardware_tier is not None:
        updates["OLLAMA_HARDWARE_TIER"] = data.ollama_hardware_tier

    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No updates provided")

    ok, msg = write_env(updates)
    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)
    return {"ok": True, "message": "AI config updated. Restart the API for changes to take effect."}


class OllamaTestRequest(BaseModel):
    """Test Ollama with a custom base URL."""

    base_url: str = Field(..., min_length=1)


@router.post("/ai/providers/ollama/test")
async def admin_ollama_test(data: OllamaTestRequest, current_user: AdminUser):
    """Test Ollama connectivity with a given base URL (before saving config)."""
    from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider

    p = OllamaProvider(base_url=data.base_url, model="")
    ok, msg = await p.health_check()
    return {"ok": ok, "message": msg}


@router.get("/ai/providers/ollama/health")
async def admin_ollama_health(current_user: AdminUser):
    """Check Ollama connectivity."""
    from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider

    s = get_settings()
    if not s.ollama_enabled:
        return {"ok": False, "message": "Ollama is not enabled"}
    p = OllamaProvider(base_url=s.ollama_base_url, model=s.ollama_model_default)
    ok, msg = await p.health_check()
    return {"ok": ok, "message": msg}


@router.get("/ai/providers/ollama/models")
async def admin_ollama_models(current_user: AdminUser):
    """List available Ollama models (refresh/sync)."""
    from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider

    s = get_settings()
    if not s.ollama_enabled:
        return {"models": [], "message": "Ollama is not enabled"}
    p = OllamaProvider(base_url=s.ollama_base_url, model=s.ollama_model_default)
    try:
        models = await p.list_models()
        return {
            "models": [{"name": m.get("name"), "size": m.get("size")} for m in models],
            "base_url": s.ollama_base_url,
        }
    except Exception as e:
        return {"models": [], "error": str(e)}


# --- Embeddings / RAG admin ---


@router.get("/ai/embeddings")
async def admin_embeddings_config(current_user: AdminUser):
    """Embeddings and RAG config."""
    from authora.services.embedding_service import get_embedding_provider, is_embeddings_configured

    s = get_settings()
    provider = get_embedding_provider()
    return {
        "embeddings_enabled": is_embeddings_configured(),
        "embeddings_provider": s.embeddings_provider,
        "ollama_embedding_model": s.ollama_embedding_model,
        "ollama_embedding_base_url": s.ollama_embedding_base_url or s.ollama_base_url,
        "rag_max_chunks": s.rag_max_chunks,
        "rag_chunk_size": s.rag_chunk_size,
        "provider_ok": (await provider.health_check())[0] if provider else False,
    }


@router.get("/ai/embeddings/ollama/health")
async def admin_embeddings_ollama_health(current_user: AdminUser):
    """Check Ollama embeddings connectivity."""
    from authora.infrastructure.embedding_provider.ollama_embedding_provider import (
        OllamaEmbeddingProvider,
    )

    s = get_settings()
    base_url = s.ollama_embedding_base_url or s.ollama_base_url
    p = OllamaEmbeddingProvider(base_url=base_url, model=s.ollama_embedding_model)
    ok, msg = await p.health_check()
    return {"ok": ok, "message": msg}


@router.get("/ai/embeddings/ollama/models")
async def admin_embeddings_ollama_models(current_user: AdminUser):
    """List Ollama embedding models."""
    from authora.infrastructure.embedding_provider.ollama_embedding_provider import (
        OllamaEmbeddingProvider,
    )

    s = get_settings()
    base_url = s.ollama_embedding_base_url or s.ollama_base_url
    p = OllamaEmbeddingProvider(base_url=base_url, model=s.ollama_embedding_model)
    try:
        models = await p.list_embedding_models()
        return {"models": [{"name": m.get("name")} for m in models], "base_url": base_url}
    except Exception as e:
        return {"models": [], "error": str(e)}


# --- Model role mapping (Ollama task→model assignments) ---


@router.get("/ai/model-roles")
async def admin_ai_model_roles(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get role→model mappings, hardware tier, available Ollama models, and fallback chains."""
    from authora.services.ai_model_settings import get_ai_model_role_overrides
    from authora.services.model_role_registry import (
        CLOUD_FALLBACK_MODELS,
        OLLAMA_DEFAULT_MODELS,
        ROLE_IDS,
        get_all_role_mappings,
    )
    from authora.services.hardware_tier import get_hardware_tier, TIER_LABELS, TIER_DESCRIPTIONS
    from authora.services.hardware_model_mapping import (
        get_tier_recommended_mapping,
        get_fallback_chain_for_role,
        apply_fallback_to_mappings,
        get_rag_limits_for_tier,
    )
    from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider

    s = get_settings()
    db_overrides = await get_ai_model_role_overrides(db)
    mappings = get_all_role_mappings(db_overrides=db_overrides)

    profile = get_hardware_tier(getattr(s, "ollama_hardware_tier", None))
    tier_recommended = get_tier_recommended_mapping(profile.tier)
    fallback_chains = {role: get_fallback_chain_for_role(role) for role in ROLE_IDS}
    rag_limits = get_rag_limits_for_tier(profile.tier)

    ollama_models: list[dict[str, Any]] = []
    available_names: set[str] = set()
    if s.ollama_enabled:
        try:
            p = OllamaProvider(base_url=s.ollama_base_url, model=s.ollama_model_default)
            raw = await p.list_models()
            ollama_models = [{"name": m.get("name"), "size": m.get("size")} for m in raw]
            available_names = {m.get("name") for m in raw if m.get("name")}
        except Exception:
            ollama_models = []

    effective_mappings = mappings
    if s.ollama_enabled and available_names:
        current = {r: mappings[r]["ollama"] for r in ROLE_IDS}
        effective = apply_fallback_to_mappings(current, available_names, profile.tier)
        effective_mappings = {
            r: {"ollama": effective[r], **{k: v for k, v in mappings[r].items() if k != "ollama"}}
            for r in ROLE_IDS
        }

    return {
        "roles": ROLE_IDS,
        "mappings": mappings,
        "effective_mappings": effective_mappings,
        "defaults": OLLAMA_DEFAULT_MODELS,
        "tier_recommended": tier_recommended,
        "cloud_fallbacks": CLOUD_FALLBACK_MODELS,
        "ollama_models": ollama_models,
        "ollama_base_url": s.ollama_base_url if s.ollama_enabled else None,
        "db_overrides": db_overrides,
        "hardware_tier": {
            "id": profile.tier,
            "label": TIER_LABELS.get(profile.tier, profile.tier),
            "description": TIER_DESCRIPTIONS.get(profile.tier, ""),
            "source": profile.source,
            "detection_message": profile.detection_message,
            "ram_gb": profile.total_ram_gb,
            "vram_gb": profile.vram_gb,
        },
        "fallback_chains": fallback_chains,
        "rag_limits": rag_limits,
    }


class ModelRoleUpdate(BaseModel):
    mappings: dict[str, str] = Field(..., description="Role ID → model name (e.g. quick_assist_model: qwen3:4b)")


@router.put("/ai/model-roles")
async def admin_update_model_roles(
    data: ModelRoleUpdate,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update role→model overrides (stored in Setting)."""
    from authora.services.ai_model_settings import save_ai_model_role_overrides

    saved = await save_ai_model_role_overrides(db, data.mappings)
    await db.commit()
    return {"ok": True, "mappings": saved}


@router.post("/ai/model-roles/apply-recommended")
async def admin_apply_recommended_model_roles(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Apply hardware-tier recommended mapping, with fallback when models missing."""
    from authora.services.ai_model_settings import save_ai_model_role_overrides
    from authora.services.hardware_tier import get_hardware_tier
    from authora.services.hardware_model_mapping import (
        get_tier_recommended_mapping,
        apply_fallback_to_mappings,
        get_available_ollama_models,
    )
    from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider

    s = get_settings()
    if not s.ollama_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ollama is not enabled")

    profile = get_hardware_tier(getattr(s, "ollama_hardware_tier", None))
    recommended = get_tier_recommended_mapping(profile.tier)
    available = await get_available_ollama_models(s.ollama_base_url)
    effective = apply_fallback_to_mappings(recommended, available, profile.tier)
    saved = await save_ai_model_role_overrides(db, effective)
    await db.commit()
    return {"ok": True, "mappings": saved, "tier": profile.tier}


# --- Project template management ---


@router.get("/templates")
async def admin_list_templates(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_disabled: bool = Query(False),
):
    """List all project templates (admin, includes disabled)."""
    q = select(ProjectTemplate).order_by(ProjectTemplate.sort_order.asc(), ProjectTemplate.name.asc())
    if not include_disabled:
        q = q.where(ProjectTemplate.is_disabled.is_(False))
    result = await db.execute(q)
    templates = result.scalars().all()
    return {
        "templates": [
            {
                "id": str(t.id),
                "slug": t.slug,
                "category": t.category,
                "parent_id": str(t.parent_id) if t.parent_id else None,
                "name": t.name,
                "description": t.description,
                "book_type": t.book_type,
                "genre": t.genre,
                "structure_framework": t.structure_framework,
                "sort_order": t.sort_order,
                "is_featured": t.is_featured,
                "is_disabled": t.is_disabled,
            }
            for t in templates
        ],
    }


class AdminTemplateUpdate(BaseModel):
    """Update template (admin)."""

    name: str | None = None
    description: str | None = None
    who_it_is_for: str | None = None
    expected_outcome: str | None = None
    suggested_workflow: str | None = None
    book_type: str | None = None
    genre: str | None = None
    structure_framework: str | None = None
    sort_order: int | None = None
    is_featured: bool | None = None
    is_disabled: bool | None = None
    default_structure: dict | None = None
    default_milestones: list | None = None
    setup_questions: list | None = None
    chapter_skeletons: list | None = None


@router.patch("/templates/{template_id}")
async def admin_update_template(
    template_id: uuid.UUID,
    data: AdminTemplateUpdate,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update template (admin)."""
    result = await db.execute(select(ProjectTemplate).where(ProjectTemplate.id == template_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    if data.name is not None:
        t.name = data.name
    if data.description is not None:
        t.description = data.description
    if data.who_it_is_for is not None:
        t.who_it_is_for = data.who_it_is_for
    if data.expected_outcome is not None:
        t.expected_outcome = data.expected_outcome
    if data.suggested_workflow is not None:
        t.suggested_workflow = data.suggested_workflow
    if data.book_type is not None:
        t.book_type = data.book_type
    if data.genre is not None:
        t.genre = data.genre
    if data.structure_framework is not None:
        t.structure_framework = data.structure_framework
    if data.sort_order is not None:
        t.sort_order = data.sort_order
    if data.is_featured is not None:
        t.is_featured = data.is_featured
    if data.is_disabled is not None:
        t.is_disabled = data.is_disabled
    if data.default_structure is not None:
        t.default_structure = data.default_structure
    if data.default_milestones is not None:
        t.default_milestones = data.default_milestones
    if data.setup_questions is not None:
        t.setup_questions = data.setup_questions
    if data.chapter_skeletons is not None:
        t.chapter_skeletons = data.chapter_skeletons
    await db.flush()
    await db.refresh(t)
    return {"id": str(t.id), "slug": t.slug, "name": t.name}


@router.post("/templates/{template_id}/duplicate")
async def admin_duplicate_template(
    template_id: uuid.UUID,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Duplicate template (admin). Creates new slug like {slug}-copy."""
    result = await db.execute(select(ProjectTemplate).where(ProjectTemplate.id == template_id))
    src = result.scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    new_slug = f"{src.slug}-copy"
    existing = (await db.execute(select(ProjectTemplate).where(ProjectTemplate.slug == new_slug))).scalar_one_or_none()
    if existing:
        new_slug = f"{src.slug}-copy-{uuid.uuid4().hex[:8]}"
    t = ProjectTemplate(
        slug=new_slug,
        category=src.category,
        parent_id=src.parent_id,
        name=f"{src.name} (copy)",
        description=src.description,
        who_it_is_for=src.who_it_is_for,
        expected_outcome=src.expected_outcome,
        suggested_workflow=src.suggested_workflow,
        book_type=src.book_type,
        genre=src.genre,
        structure_framework=src.structure_framework,
        default_structure=src.default_structure,
        default_milestones=src.default_milestones,
        default_planning_prompts=src.default_planning_prompts,
        default_accountability=src.default_accountability,
        ai_prompts=src.ai_prompts,
        export_recommendations=src.export_recommendations,
        setup_questions=src.setup_questions,
        chapter_skeletons=src.chapter_skeletons,
        sort_order=src.sort_order + 1,
        is_featured=False,
        is_disabled=False,
    )
    db.add(t)
    await db.flush()
    await db.refresh(t)
    return {"id": str(t.id), "slug": t.slug, "name": t.name}


class AdminTemplatesReorderRequest(BaseModel):
    template_ids: list[uuid.UUID] = Field(..., min_length=1)


@router.post("/templates/reorder")
async def admin_reorder_templates(
    data: AdminTemplatesReorderRequest,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Reorder templates by id list (admin)."""
    template_ids = data.template_ids
    result = await db.execute(select(ProjectTemplate).where(ProjectTemplate.id.in_(template_ids)))
    templates = {t.id: t for t in result.scalars().all()}
    for i, tid in enumerate(template_ids):
        if tid in templates:
            templates[tid].sort_order = i
    await db.flush()
    return {"ok": True}


@router.get("/templates/usage")
async def admin_template_usage(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Template usage analytics: projects and books per template."""
    from sqlalchemy import func as sql_func

    projects_q = (
        select(Project.template_id, sql_func.count(Project.id).label("count"))
        .where(Project.template_id.isnot(None))
        .group_by(Project.template_id)
    )
    books_q = (
        select(Book.template_id, sql_func.count(Book.id).label("count"))
        .where(Book.template_id.isnot(None))
        .group_by(Book.template_id)
    )
    pr = await db.execute(projects_q)
    br = await db.execute(books_q)
    by_template: dict[str, dict[str, int]] = {}
    for tid, cnt in pr.all():
        key = str(tid)
        if key not in by_template:
            by_template[key] = {"projects": 0, "books": 0}
        by_template[key]["projects"] = cnt
    for tid, cnt in br.all():
        key = str(tid)
        if key not in by_template:
            by_template[key] = {"projects": 0, "books": 0}
        by_template[key]["books"] = cnt
    return {"by_template": by_template}


# --- Writing framework management ---


@router.get("/frameworks")
async def admin_list_frameworks(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_disabled: bool = Query(False),
    book_type: str | None = Query(None, description="fiction | nonfiction"),
):
    """List all writing frameworks (admin, includes disabled)."""
    q = select(WritingFramework).order_by(WritingFramework.sort_order.asc(), WritingFramework.name.asc())
    if not include_disabled:
        q = q.where(WritingFramework.is_disabled.is_(False))
    if book_type:
        q = q.where(WritingFramework.book_type == book_type)
    result = await db.execute(q)
    frameworks = result.scalars().all()
    return {
        "frameworks": [
            {
                "id": str(f.id),
                "slug": f.slug,
                "book_type": f.book_type,
                "name": f.name,
                "description": f.description,
                "ideal_genres": f.ideal_genres,
                "sort_order": f.sort_order,
                "is_featured": f.is_featured,
                "is_disabled": f.is_disabled,
            }
            for f in frameworks
        ],
    }


class AdminFrameworkUpdate(BaseModel):
    """Update framework (admin)."""

    name: str | None = None
    description: str | None = None
    ideal_use_cases: str | None = None
    ideal_genres: list[str] | None = None
    planning_stages: list | None = None
    beat_stages: list | None = None
    chapter_structure: dict | None = None
    manuscript_scaffolding: dict | None = None
    chapter_skeletons: list | None = None
    milestone_logic: dict | None = None
    accountability_mapping: dict | None = None
    revision_checklist: list | None = None
    ai_prompt_presets: dict | None = None
    recommendation_rules: dict | None = None
    scene_prompts: dict | None = None
    sort_order: int | None = None
    is_featured: bool | None = None
    is_disabled: bool | None = None


@router.patch("/frameworks/{framework_id}")
async def admin_update_framework(
    framework_id: uuid.UUID,
    data: AdminFrameworkUpdate,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update framework (admin)."""
    result = await db.execute(select(WritingFramework).where(WritingFramework.id == framework_id))
    f = result.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Framework not found")
    for field in ["name", "description", "ideal_use_cases", "ideal_genres", "planning_stages", "beat_stages",
                  "chapter_structure", "manuscript_scaffolding", "chapter_skeletons", "milestone_logic",
                  "accountability_mapping", "revision_checklist", "ai_prompt_presets", "recommendation_rules",
                  "scene_prompts", "sort_order", "is_featured", "is_disabled"]:
        val = getattr(data, field, None)
        if val is not None:
            setattr(f, field, val)
    await db.flush()
    await db.refresh(f)
    return {"id": str(f.id), "slug": f.slug, "name": f.name}


@router.post("/frameworks/{framework_id}/duplicate")
async def admin_duplicate_framework(
    framework_id: uuid.UUID,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Duplicate framework (admin). Creates new slug like {slug}-copy."""
    result = await db.execute(select(WritingFramework).where(WritingFramework.id == framework_id))
    src = result.scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Framework not found")
    new_slug = f"{src.slug}-copy"
    existing = (await db.execute(select(WritingFramework).where(WritingFramework.slug == new_slug))).scalar_one_or_none()
    if existing:
        new_slug = f"{src.slug}-copy-{uuid.uuid4().hex[:8]}"
    f = WritingFramework(
        slug=new_slug,
        book_type=src.book_type,
        name=f"{src.name} (copy)",
        description=src.description,
        ideal_use_cases=src.ideal_use_cases,
        ideal_genres=src.ideal_genres,
        planning_stages=src.planning_stages,
        beat_stages=src.beat_stages,
        chapter_structure=src.chapter_structure,
        manuscript_scaffolding=src.manuscript_scaffolding,
        chapter_skeletons=src.chapter_skeletons,
        milestone_logic=src.milestone_logic,
        accountability_mapping=src.accountability_mapping,
        revision_checklist=src.revision_checklist,
        ai_prompt_presets=src.ai_prompt_presets,
        recommendation_rules=src.recommendation_rules,
        scene_prompts=src.scene_prompts,
        sort_order=src.sort_order + 1,
        is_featured=False,
        is_disabled=False,
    )
    db.add(f)
    await db.flush()
    await db.refresh(f)
    return {"id": str(f.id), "slug": f.slug, "name": f.name}


class AdminFrameworksReorderRequest(BaseModel):
    framework_ids: list[uuid.UUID] = Field(..., min_length=1)


@router.post("/frameworks/reorder")
async def admin_reorder_frameworks(
    data: AdminFrameworksReorderRequest,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Reorder frameworks by id list (admin)."""
    fids = data.framework_ids
    result = await db.execute(select(WritingFramework).where(WritingFramework.id.in_(fids)))
    frameworks = {f.id: f for f in result.scalars().all()}
    for i, fid in enumerate(fids):
        if fid in frameworks:
            frameworks[fid].sort_order = i
    await db.flush()
    return {"ok": True}


@router.get("/frameworks/usage")
async def admin_framework_usage(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Framework usage analytics: books per framework."""
    from sqlalchemy import func as sql_func

    books_q = (
        select(Book.framework_id, sql_func.count(Book.id).label("count"))
        .where(Book.framework_id.isnot(None))
        .group_by(Book.framework_id)
    )
    br = await db.execute(books_q)
    by_framework: dict[str, int] = {}
    for fid, cnt in br.all():
        by_framework[str(fid)] = cnt
    return {"by_framework": by_framework}


@router.get("/ai/model-roles/validate")
async def admin_validate_model_roles(
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Validate that selected models exist in Ollama."""
    from authora.services.ai_model_settings import get_ai_model_role_overrides
    from authora.services.model_role_registry import get_ollama_model_for_role, ROLE_IDS
    from authora.infrastructure.ai_provider.ollama_provider import OllamaProvider

    s = get_settings()
    if not s.ollama_enabled:
        return {"valid": False, "message": "Ollama is not enabled", "results": {}}

    db_overrides = await get_ai_model_role_overrides(db)
    try:
        p = OllamaProvider(base_url=s.ollama_base_url, model=s.ollama_model_default)
        available = {m.get("name") for m in await p.list_models() if m.get("name")}
    except Exception as e:
        return {"valid": False, "message": str(e), "results": {}}

    results: dict[str, dict[str, Any]] = {}
    all_valid = True
    for role in ROLE_IDS:
        model = get_ollama_model_for_role(role, db_overrides=db_overrides)
        found = model in available
        if not found:
            all_valid = False
        results[role] = {"model": model, "valid": found}

    return {"valid": all_valid, "results": results, "available_count": len(available)}
