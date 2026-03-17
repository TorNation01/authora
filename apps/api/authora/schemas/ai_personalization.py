"""AI personalization schemas."""

from pydantic import BaseModel, Field


class StyleProfile(BaseModel):
    """Learned or user-set writing style profile."""

    voice: str | None = Field(None, description="Author voice notes (e.g. 'literary, introspective')")
    tone: str | None = Field(None, description="Preferred tone (formal, casual, lyrical, etc.)")
    vocabulary: str | None = Field(None, description="Vocabulary preferences (e.g. 'avoid jargon, prefer simple words')")
    sentence_style: str | None = Field(None, description="Sentence structure (short punchy, flowing, varied)")


class AIPersonalizationUpdate(BaseModel):
    """Update AI personalization settings."""

    enabled: bool | None = Field(None, description="Turn personalization on or off")
    tone_preferences: list[str] | None = Field(None, description="Preferred tones (e.g. formal, conversational)")
    style_profile: StyleProfile | None = Field(None, description="Style profile (voice, tone, vocabulary, sentence_style)")


class AIPersonalizationResponse(BaseModel):
    """AI personalization settings response."""

    enabled: bool = False
    tone_preferences: list[str] = Field(default_factory=list)
    style_profile: StyleProfile | None = None
    updated_at: str | None = None


class AIPersonalizationLearnRequest(BaseModel):
    """Request to learn style from a book."""

    book_id: str = Field(..., description="Book UUID to learn style from")
