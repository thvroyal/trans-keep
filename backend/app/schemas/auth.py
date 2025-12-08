"""Authentication schemas for request/response validation"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    """JWT token response"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until expiration


class UserInfo(BaseModel):
    """User information response"""

    id: UUID
    email: EmailStr
    name: str | None
    picture_url: str | None
    subscription_tier: str
    created_at: datetime

    class Config:
        from_attributes = True


class GoogleOAuthCallback(BaseModel):
    """Google OAuth callback request"""

    code: str
    state: str | None = None

