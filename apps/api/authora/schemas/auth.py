"""Auth schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from authora.core.password_policy import MIN_LENGTH, password_problem


def _email_like(v: str) -> str:
    """Accept email-like strings including @authora.local for testing."""
    v = (v or "").strip().lower()
    if "@" in v and v.index("@") > 0 and len(v) > v.index("@") + 1:
        return v
    raise ValueError("Invalid email format")


class UserCreate(BaseModel):
    """User registration."""

    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=MIN_LENGTH, max_length=128)
    display_name: str | None = None
    referral_code: str | None = None
    affiliate_code: str | None = None
    invite_code: str | None = None
    turnstile_token: str | None = None
    # Anonymous visit id (cookie `av_id`, set by the Next middleware) so a
    # signup can be attributed to the page view that produced it.
    visitor_id: str | None = Field(None, max_length=64)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _email_like(v)

    @model_validator(mode="after")
    def validate_password_strength(self) -> "UserCreate":
        problem = password_problem(self.password, self.email)
        if problem:
            raise ValueError(problem)
        return self


class UserLogin(BaseModel):
    """User login."""

    email: str = Field(..., min_length=3, max_length=255)
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _email_like(v)


class UserResponse(BaseModel):
    """User in API response."""

    id: UUID
    email: str
    display_name: str | None
    created_at: datetime
    is_admin: bool = False
    email_verified: bool = True

    model_config = {"from_attributes": True}


class VerifyEmailRequest(BaseModel):
    """Token from the verification link."""

    token: str = Field(..., min_length=16, max_length=255)


class VerifyEmailResponse(BaseModel):
    verified: bool
    already_verified: bool = False
    email: str | None = None


class Token(BaseModel):
    """JWT token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """JWT payload."""

    sub: str  # user_id
    exp: datetime
    type: str  # access | refresh


class RefreshRequest(BaseModel):
    """Refresh token request body."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request body."""

    refresh_token: str


class UserUpdate(BaseModel):
    """User profile update."""

    display_name: str | None = Field(None, max_length=255)


class PasswordChange(BaseModel):
    """Password change request."""

    current_password: str
    new_password: str = Field(..., min_length=MIN_LENGTH, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        problem = password_problem(v)
        if problem:
            raise ValueError(problem)
        return v
