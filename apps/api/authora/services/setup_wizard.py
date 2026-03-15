"""Setup wizard service - validation, connection testing, config writing, finalization."""

import asyncio
import os
import re
import secrets
import subprocess
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from authora.schemas.setup_schema import (
    SetupAdmin,
    SetupAI,
    SetupApplyRequest,
    SetupFinalizeRequest,
    SetupTestRequest,
    SetupTestResult,
    SetupValidationResult,
)


# Keys that should never be logged
SECRET_KEYS = {"secret_key", "admin_password", "openai_api_key", "anthropic_api_key", "smtp_password"}


def _get_env_path() -> Path:
    root = Path(__file__).resolve().parent.parent.parent.parent.parent
    return root / ".env"


def _parse_env(content: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([^#=]+)=(.*)$", line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip().strip('"').strip("'")
            result[key] = val
    return result


def _serialize_env(data: dict[str, str]) -> str:
    lines = []
    for k, v in sorted(data.items()):
        if " " in str(v) or "#" in str(v) or not v:
            v = f'"{v}"'
        lines.append(f"{k}={v}")
    return "\n".join(lines)


def write_env(updates: dict[str, str]) -> tuple[bool, str]:
    """
    Safely update .env file. Merges with existing, never overwrites entire file.
    Returns (success, message).
    """
    env_path = _get_env_path()
    existing: dict[str, str] = {}
    if env_path.exists():
        try:
            content = env_path.read_text(encoding="utf-8")
            existing = _parse_env(content)
        except Exception as e:
            return False, f"Cannot read .env: {e}"

    for k, v in updates.items():
        if v is not None and v != "":
            existing[k] = str(v)

    try:
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text(_serialize_env(existing) + "\n", encoding="utf-8")
        return True, f"Updated {env_path}"
    except Exception as e:
        return False, str(e)


def validate_database_url(url: str) -> SetupValidationResult:
    if not url or len(url) < 10:
        return SetupValidationResult(valid=False, message="Database URL too short")
    if not url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        return SetupValidationResult(valid=False, message="Must be PostgreSQL URL")
    return SetupValidationResult(valid=True)


def validate_redis_url(url: str) -> SetupValidationResult:
    if not url or len(url) < 10:
        return SetupValidationResult(valid=False, message="Redis URL too short")
    if not url.startswith("redis://") and not url.startswith("rediss://"):
        return SetupValidationResult(valid=False, message="Must be Redis URL")
    return SetupValidationResult(valid=True)


async def test_database_connection(url: str) -> SetupValidationResult:
    try:
        db_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        engine = create_async_engine(db_url, pool_pre_ping=True, pool_size=1)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return SetupValidationResult(valid=True)
    except Exception as e:
        return SetupValidationResult(valid=False, message=str(e))


async def test_redis_connection(url: str) -> SetupValidationResult:
    try:
        from redis.asyncio import Redis

        client = Redis.from_url(url)
        await client.ping()
        await client.aclose()
        return SetupValidationResult(valid=True)
    except ImportError:
        return SetupValidationResult(valid=False, message="redis package not installed")
    except Exception as e:
        return SetupValidationResult(valid=False, message=str(e))


async def test_connections(req: SetupTestRequest) -> SetupTestResult:
    result = SetupTestResult()
    if req.database_url:
        result.database = await test_database_connection(req.database_url)
    if req.redis_url:
        result.redis = await test_redis_connection(req.redis_url)
    return result


def apply_config(req: SetupApplyRequest) -> tuple[bool, str]:
    """Apply config to .env file."""
    updates: dict[str, str] = {}

    if req.branding:
        updates["BRANDING_PRODUCT_NAME"] = req.branding.product_name
        updates["BRANDING_TAGLINE"] = req.branding.tagline

    if req.domain:
        updates["DOMAIN"] = req.domain.domain
        # SSL is typically handled by reverse proxy; we can store a flag
        if req.domain.use_ssl:
            updates["FORCE_HTTPS"] = "true"

    if req.database_url:
        updates["DATABASE_URL"] = req.database_url

    if req.redis_url:
        updates["REDIS_URL"] = req.redis_url

    if req.storage:
        updates["STORAGE_PROVIDER"] = req.storage.storage_provider
        updates["STORAGE_LOCAL_PATH"] = req.storage.storage_local_path
        if req.storage.s3_bucket:
            updates["S3_BUCKET"] = req.storage.s3_bucket
        if req.storage.r2_bucket:
            updates["R2_BUCKET"] = req.storage.r2_bucket
        if req.storage.r2_account_id:
            updates["R2_ACCOUNT_ID"] = req.storage.r2_account_id
        updates["AWS_REGION"] = req.storage.aws_region

    if req.ai:
        updates["AI_PROVIDER"] = req.ai.ai_provider
        updates["AI_MODEL"] = req.ai.ai_model
        if req.ai.openai_api_key:
            updates["OPENAI_API_KEY"] = req.ai.openai_api_key
        if req.ai.anthropic_api_key:
            updates["ANTHROPIC_API_KEY"] = req.ai.anthropic_api_key

    if req.email and req.email.enabled:
        if req.email.smtp_host:
            updates["SMTP_HOST"] = req.email.smtp_host
        if req.email.smtp_port:
            updates["SMTP_PORT"] = str(req.email.smtp_port)
        if req.email.smtp_user:
            updates["SMTP_USER"] = req.email.smtp_user
        if req.email.smtp_password:
            updates["SMTP_PASSWORD"] = req.email.smtp_password
        if req.email.from_email:
            updates["FROM_EMAIL"] = req.email.from_email

    if req.preferences:
        updates["BACKUP_ENABLED"] = str(req.preferences.backup_enabled).lower()
        updates["BACKUP_RETENTION_DAYS"] = str(req.preferences.backup_retention_days)
        updates["REMINDER_ENABLED"] = str(req.preferences.reminder_enabled).lower()
        updates["REMINDER_DEFAULT_TIME"] = req.preferences.reminder_default_time
        updates["ANALYTICS_ENABLED"] = str(req.preferences.analytics_enabled).lower()
        updates["TELEMETRY_ENABLED"] = str(req.preferences.telemetry_enabled).lower()

    if req.mode:
        updates["DEPLOYMENT_MODE"] = "standalone"
        if req.mode.mode == "cloud":
            updates["DEPLOYMENT_MODE"] = "standalone"  # still standalone, cloud just affects storage

    if req.secret_key:
        updates["SECRET_KEY"] = req.secret_key
    else:
        try:
            existing = _parse_env(_get_env_path().read_text(encoding="utf-8")) if _get_env_path().exists() else {}
        except Exception:
            existing = {}
        if "SECRET_KEY" not in existing or not existing.get("SECRET_KEY") or "change-me" in (existing.get("SECRET_KEY") or ""):
            updates["SECRET_KEY"] = secrets.token_hex(32)

    return write_env(updates)


async def run_migrations(database_url: str) -> tuple[bool, str]:
    """Run alembic migrations."""
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    # alembic.ini lives in apps/api
    root = Path(__file__).resolve().parent.parent.parent
    try:
        proc = await asyncio.create_subprocess_exec(
            "alembic",
            "upgrade",
            "head",
            cwd=str(root),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            return False, (stderr.decode() or stdout.decode() or "Migration failed")
        return True, "Migrations applied"
    except FileNotFoundError:
        return False, "alembic not found"
    except Exception as e:
        return False, str(e)


async def seed_templates(db_url: str) -> tuple[bool, str]:
    """Seed starter templates into settings."""
    try:
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

        from authora.models import Setting

        engine = create_async_engine(
            db_url.replace("postgresql://", "postgresql+asyncpg://", 1),
            pool_pre_ping=True,
        )
        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session:
            # Check if already seeded
            r = await session.execute(select(Setting).where(Setting.key == "setup_templates_seeded"))
            if r.scalar_one_or_none():
                await engine.dispose()
                return True, "Templates already seeded"

            from authora.scripts.demo_templates_data import FICTION_TEMPLATE, NONFICTION_TEMPLATE

            templates = [
                Setting(key="template_fiction_planner", value=FICTION_TEMPLATE),
                Setting(key="template_nonfiction_planner", value=NONFICTION_TEMPLATE),
            ]
            for t in templates:
                session.merge(t)
            session.merge(Setting(key="setup_templates_seeded", value={"seeded": True}))
            await session.commit()
        await engine.dispose()
        return True, "Starter templates seeded"
    except Exception as e:
        return False, str(e)


async def create_admin_user(db_url: str, admin: SetupAdmin) -> tuple[bool, str]:
    """Create admin user in database."""
    try:
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

        from authora.models import Setting, User
        from authora.services.auth import create_user

        engine = create_async_engine(
            db_url.replace("postgresql://", "postgresql+asyncpg://", 1),
            pool_pre_ping=True,
        )
        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session:
            r = await session.execute(select(User).where(User.email == admin.admin_email))
            if r.scalar_one_or_none():
                await engine.dispose()
                return False, "User with this email already exists"

            user = await create_user(
                session,
                email=admin.admin_email,
                password=admin.admin_password,
                display_name=admin.admin_display_name or "Admin",
            )
            user.is_admin = True
            await session.flush()

            setting = Setting(key="setup_complete", value={"complete": True})
            session.merge(setting)
            from datetime import datetime, timezone

            baseline = Setting(
                key="health_baseline",
                value={
                    "setup_at": datetime.now(timezone.utc).isoformat(),
                    "database": "connected",
                    "admin_created": True,
                },
            )
            session.merge(baseline)
            await session.commit()
            user_id = str(user.id)
        await engine.dispose()
        return True, user_id
    except Exception as e:
        return False, str(e)


async def finalize_setup(req: SetupFinalizeRequest) -> dict:
    """
    Run finalization: migrations, seed templates, create admin.
    Returns status dict with success flags and messages.
    """
    results: dict = {
        "migrations": {"success": False, "message": ""},
        "templates": {"success": False, "message": ""},
        "admin": {"success": False, "message": "", "user_id": None},
    }

    if req.run_migrations:
        ok, msg = await run_migrations(req.database_url)
        results["migrations"] = {"success": ok, "message": msg}
        if not ok:
            return results

    if req.seed_templates:
        ok, msg = await seed_templates(req.database_url)
        results["templates"] = {"success": ok, "message": msg}

    ok, msg = await create_admin_user(req.database_url, req.admin)
    results["admin"] = {
        "success": ok,
        "message": msg if not ok else "Admin created",
        "user_id": msg if ok else None,
    }
    return results
