"""Setup wizard API - first-run configuration. Standalone mode only."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from authora.config import get_settings
from authora.models import Setting, User
from authora.schemas.setup_schema import (
    SetupAdmin,
    SetupAI,
    SetupApplyRequest,
    SetupFinalizeRequest,
    SetupTestRequest,
)
from authora.services.setup_wizard import (
    apply_config,
    finalize_setup,
    test_connections,
)

router = APIRouter(prefix="/setup", tags=["setup"])


def _require_standalone():
    if not get_settings().is_standalone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setup wizard is only available in standalone mode",
        )


@router.get("/status")
async def setup_status():
    """Check if setup is complete. Works even when DB is not yet configured."""
    _require_standalone()
    from authora.database import async_session_factory

    try:
        async with async_session_factory() as db:
            result = await db.execute(select(func.count(User.id)))
            user_count = result.scalar() or 0
            result = await db.execute(select(Setting).where(Setting.key == "setup_complete"))
            setting = result.scalar_one_or_none()
            complete = (setting and setting.value.get("complete") is True) or user_count > 0
            return {
                "setup_complete": complete,
                "has_users": user_count > 0,
                "can_connect": True,
            }
    except Exception:
        return {
            "setup_complete": False,
            "has_users": False,
            "can_connect": False,
        }


@router.post("/test")
async def setup_test(req: SetupTestRequest):
    """Test database and/or Redis connections."""
    _require_standalone()
    result = await test_connections(req)
    return result.model_dump()


@router.post("/apply")
async def setup_apply(req: SetupApplyRequest):
    """Apply configuration to .env file."""
    _require_standalone()
    success, message = apply_config(req)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)
    return {"success": True, "message": message}


@router.post("/finalize")
async def setup_finalize(req: SetupFinalizeRequest):
    """Run migrations, seed templates, create admin. Rerun-safe (skips if users exist)."""
    _require_standalone()
    result = await finalize_setup(req)
    if not result["admin"]["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["admin"]["message"],
        )
    return {
        "success": True,
        "results": result,
        "message": "Setup complete. Restart the application to apply configuration changes.",
    }


# Legacy endpoint - kept for backward compatibility
@router.post("/complete")
async def setup_complete_legacy(data: dict):
    """Legacy: Complete setup with admin only. Prefer /finalize for full wizard."""
    _require_standalone()
    admin_email = data.get("admin_email")
    admin_password = data.get("admin_password")
    if not admin_email or not admin_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="admin_email and admin_password required")

    admin = SetupAdmin(
        admin_email=admin_email,
        admin_password=admin_password,
        admin_display_name=data.get("admin_display_name", "Admin"),
    )
    settings = get_settings()
    req = SetupFinalizeRequest(
        database_url=settings.database_url,
        admin=admin,
        run_migrations=True,
        seed_templates=True,
    )
    result = await finalize_setup(req)
    if not result["admin"]["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["admin"]["message"])
    return {"message": "Setup complete", "user_id": result["admin"]["user_id"]}
