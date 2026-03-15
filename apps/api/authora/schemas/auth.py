"""Auth schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """User registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str | None = None


class UserLogin(BaseModel):
    """User login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User in API response."""

    id: UUID
    email: str
    display_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


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
    new_password: str = Field(..., min_length=8, max_length=128)
