"""Authentication router for Google OAuth and JWT token management"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated
from urllib.parse import urlencode
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.auth.transport import requests
from google.oauth2 import id_token
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_db
from app.models.user import SubscriptionTier, User
from app.schemas.auth import GoogleOAuthCallback, TokenResponse, UserInfo

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

# Google OAuth endpoints
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


def create_access_token(user_id: str, tenant_id: str, settings: Settings) -> tuple[str, int]:
    """
    Create a JWT access token for a user.
    
    Args:
        user_id: User's unique identifier
        tenant_id: Tenant's unique identifier
        settings: Application settings instance
    
    Returns:
        Tuple of (token_string, expires_in_seconds)
    """
    expiration = datetime.now(timezone.utc) + timedelta(
        hours=settings.jwt_expiration_hours
    )
    payload = {
        "sub": user_id,  # Subject (user ID)
        "tenant_id": tenant_id,
        "exp": expiration,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(
        payload, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )
    expires_in = int(settings.jwt_expiration_hours * 3600)
    return token, expires_in


async def get_or_create_user(
    db: AsyncSession, google_id: str, email: str, name: str | None, picture_url: str | None
) -> User:
    """
    Get existing user or create new user from Google OAuth data.
    
    Returns:
        User instance
    """
    # Try to find existing user by google_id
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    if user:
        # Update user info if changed
        if user.email != email or user.name != name or user.picture_url != picture_url:
            user.email = email
            user.name = name
            user.picture_url = picture_url
            user.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(user)
        return user

    # Check if user exists with same email (edge case: user changed Google account)
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        # Update existing user with Google ID
        existing_user.google_id = google_id
        existing_user.name = name
        existing_user.picture_url = picture_url
        existing_user.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(existing_user)
        return existing_user

    # Create new user
    new_user = User(
        google_id=google_id,
        email=email,
        name=name,
        picture_url=picture_url,
        subscription_tier=SubscriptionTier.FREE,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/google")
async def initiate_google_oauth(
    settings: Settings = Depends(get_settings),
):
    """
    Initiate Google OAuth flow by redirecting to Google consent screen.
    
    Returns redirect URL for frontend to navigate to.
    """
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured",
        )

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Build Google OAuth URL
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": "http://localhost:5173/auth/callback",  # Frontend callback (Vite dev server)
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    return {"auth_url": auth_url, "state": state}


@router.post("/google/callback")
async def google_oauth_callback(
    callback: GoogleOAuthCallback,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """
    Handle Google OAuth callback by exchanging code for ID token,
    verifying it, and creating/updating user.
    
    Returns JWT access token.
    """
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured",
        )

    try:
        # Exchange authorization code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": callback.code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": "http://localhost:5173/auth/callback",
                    "grant_type": "authorization_code",
                },
            )
            token_response.raise_for_status()
            token_data = token_response.json()

        id_token_str = token_data.get("id_token")
        if not id_token_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No ID token in response",
            )

        # Verify ID token
        request_obj = requests.Request()
        id_info = id_token.verify_oauth2_token(
            id_token_str, request_obj, settings.google_client_id
        )

        # Extract user info from ID token
        google_id = id_info.get("sub")
        email = id_info.get("email")
        name = id_info.get("name")
        picture_url = id_info.get("picture")

        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID token: missing user info",
            )

        # Get or create user
        user = await get_or_create_user(db, google_id, email, name, picture_url)

        # Generate JWT token
        token, expires_in = create_access_token(str(user.id), str(user.tenant_id), settings)

        return TokenResponse(access_token=token, expires_in=expires_in)

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange code: {e.response.text}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID token: {str(e)}",
        )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token clearing).
    
    Note: Since we use stateless JWT tokens, logout is handled client-side
    by removing the token. In production, you might want to maintain a
    token blacklist in Redis.
    """
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> UserInfo:
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Decode and verify JWT token
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        # Get user from database
        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        return UserInfo.model_validate(user)

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

