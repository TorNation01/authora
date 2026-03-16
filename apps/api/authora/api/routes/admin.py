"""Admin/operator control layer - user management, feature flags, monitoring, etc."""

import uuid
from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    Reminder,
    Setting,
    SetupState,
    UsageRecord,
    User,
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
    }


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
