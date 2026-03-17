"""Community schemas: profiles, groups, feedback."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# --- Profile & settings ---

class CommunitySettingsResponse(BaseModel):
    """User community settings (privacy-first, all optional)."""

    profile_visibility: str = Field(..., description="private | friends_only | public")
    profile_slug: str | None = None
    share_progress: bool = Field(default=False, description="Opt-in to share progress")

    model_config = {"from_attributes": True}


class CommunitySettingsUpdate(BaseModel):
    """Update community settings."""

    profile_visibility: str | None = Field(None, pattern="^(private|friends_only|public)$")
    profile_slug: str | None = Field(None, max_length=100)
    share_progress: bool | None = None


class PublicProfileResponse(BaseModel):
    """Public profile (only when profile_visibility is public)."""

    id: UUID
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    profile_slug: str | None

    model_config = {"from_attributes": True}


class ProgressShareResponse(BaseModel):
    """Shared progress (only when user opts in)."""

    total_words: int
    total_books: int
    total_chapters: int

    model_config = {"from_attributes": True}


# --- Writing groups ---

class WritingGroupCreate(BaseModel):
    """Create writing group."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    is_public: bool = False


class WritingGroupResponse(BaseModel):
    """Writing group in API response."""

    id: UUID
    name: str
    description: str | None
    created_by_id: UUID
    is_public: bool
    member_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class WritingGroupInviteCreate(BaseModel):
    """Invite to writing group."""

    email: str = Field(..., min_length=1, max_length=255)


# --- Feedback threads ---

class FeedbackThreadCreate(BaseModel):
    """Create feedback thread."""

    target_type: str = Field(..., pattern="^(chapter|shared_excerpt|project)$")
    target_id: str = Field(..., max_length=100)
    title: str | None = Field(None, max_length=255)


class FeedbackThreadResponse(BaseModel):
    """Feedback thread in API response."""

    id: UUID
    project_id: UUID
    target_type: str
    target_id: str
    title: str | None
    created_by_id: UUID
    comment_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackCommentCreate(BaseModel):
    """Create feedback comment."""

    body: str = Field(..., min_length=1, max_length=10000)


class FeedbackCommentResponse(BaseModel):
    """Feedback comment in API response."""

    id: UUID
    thread_id: UUID
    user_id: UUID
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}
