"""Content API - templates, messages, copy. Public endpoints."""

from fastapi import APIRouter, Query

from authora.content import (
    get_all_templates,
    get_template_by_id,
    get_templates_by_type,
    get_random_encouragement,
    get_random_recovery_nudge,
    get_random_celebration,
    ONBOARDING_COPY,
    HELP_TOOLTIPS,
    EMPTY_STATE_COPY,
    AI_EXPLANATION_COPY,
    ENCOURAGEMENT_MESSAGES,
    RECOVERY_NUDGES,
    CELEBRATION_MESSAGES,
)

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/templates")
async def list_templates(book_type: str | None = Query(None, description="Filter by fiction or nonfiction")):
    """List all built-in project templates. Optionally filter by type."""
    if book_type:
        return get_templates_by_type(book_type)
    return get_all_templates()


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a single template by ID."""
    t = get_template_by_id(template_id)
    if not t:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Template not found")
    return t


@router.get("/messages/encouragement")
async def random_encouragement():
    """Get a random encouragement message."""
    return {"message": get_random_encouragement()}


@router.get("/messages/recovery")
async def random_recovery():
    """Get a random recovery nudge."""
    return {"message": get_random_recovery_nudge()}


@router.get("/messages/celebration")
async def random_celebration(category: str | None = Query("general", description="streak, chapter, word_count, milestone, badge, general")):
    """Get a random celebration message for the given category."""
    return {"message": get_random_celebration(category)}


@router.get("/messages/encouragement/all")
async def list_encouragement():
    """List all encouragement messages."""
    return {"messages": ENCOURAGEMENT_MESSAGES}


@router.get("/messages/recovery/all")
async def list_recovery():
    """List all recovery nudges."""
    return {"messages": RECOVERY_NUDGES}


@router.get("/messages/celebration/all")
async def list_celebration():
    """List all celebration messages by category."""
    return {"messages": CELEBRATION_MESSAGES}


@router.get("/copy/onboarding")
async def get_onboarding_copy():
    """Get onboarding copy for all steps."""
    return ONBOARDING_COPY


@router.get("/copy/tooltips")
async def get_tooltips():
    """Get help tooltips keyed by feature."""
    return HELP_TOOLTIPS


@router.get("/copy/empty-states")
async def get_empty_state_copy():
    """Get empty state copy keyed by context."""
    return EMPTY_STATE_COPY


@router.get("/copy/ai-explanations")
async def get_ai_explanations():
    """Get AI feature explanation copy."""
    return AI_EXPLANATION_COPY
