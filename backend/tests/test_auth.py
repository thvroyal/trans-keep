"""Tests for authentication endpoints"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest_asyncio
from httpx import AsyncClient
from jose import jwt

from app.config import get_settings
from app.models.user import SubscriptionTier, User

settings = get_settings()


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    user_id = uuid4()
    tenant_id = uuid4()
    return User(
        id=user_id,
        tenant_id=tenant_id,
        google_id="google_123",
        email="test@example.com",
        name="Test User",
        picture_url="https://example.com/pic.jpg",
        subscription_tier=SubscriptionTier.FREE,
        usage_this_month=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def valid_token(mock_user):
    """Create a valid JWT token for testing"""
    expiration = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": str(mock_user.id),
        "tenant_id": str(mock_user.tenant_id),
        "exp": expiration,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


class TestGoogleOAuthInitiate:
    """Tests for GET /api/v1/auth/google"""

    @pytest.mark.asyncio
    async def test_initiate_oauth_success(self, client: AsyncClient):
        """Test successful OAuth initiation"""
        with patch.object(settings, "google_client_id", "test_client_id"):
            response = await client.get("/api/v1/auth/google")
            assert response.status_code == 200
            data = response.json()
            assert "auth_url" in data
            assert "state" in data
            assert "test_client_id" in data["auth_url"]
            assert "http://localhost:5173/auth/callback" in data["auth_url"]

    @pytest.mark.asyncio
    async def test_initiate_oauth_not_configured(self, client: AsyncClient):
        """Test OAuth initiation when not configured"""
        with patch.object(settings, "google_client_id", ""):
            response = await client.get("/api/v1/auth/google")
            assert response.status_code == 500
            assert "not configured" in response.json()["detail"].lower()


class TestGoogleOAuthCallback:
    """Tests for POST /api/v1/auth/google/callback"""

    @pytest.mark.asyncio
    async def test_callback_success(self, mock_user):
        """Test successful OAuth callback"""
        # Mock Google token exchange
        mock_token_response = {
            "id_token": "mock_id_token",
            "access_token": "mock_access_token",
        }

        # Mock ID token verification
        mock_id_info = {
            "sub": "google_123",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/pic.jpg",
        }

        with patch("httpx.AsyncClient.post") as mock_post, patch(
            "google.oauth2.id_token.verify_oauth2_token"
        ) as mock_verify, patch(
            "app.routers.auth.get_or_create_user"
        ) as mock_get_user:
            # Setup mocks
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_token_response
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            mock_verify.return_value = mock_id_info
            mock_get_user.return_value = mock_user

            # TODO: Implement full async test with proper database mocking
            # For now, we'll skip the full integration test and test components separately
            pass

    @pytest.mark.asyncio
    async def test_callback_no_code(self, client: AsyncClient):
        """Test callback with missing code"""
        response = await client.post("/api/v1/auth/google/callback", json={})
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_callback_not_configured(self, client: AsyncClient):
        """Test callback when OAuth not configured"""
        with patch.object(settings, "google_client_id", ""):
            response = await client.post(
                "/api/v1/auth/google/callback",
                json={"code": "test_code"},
            )
            assert response.status_code == 500
            assert "not configured" in response.json()["detail"].lower()


class TestGetCurrentUser:
    """Tests for GET /api/v1/auth/me"""

    @pytest.mark.asyncio
    async def test_get_user_no_token(self, client: AsyncClient):
        """Test getting user without token"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_user_invalid_token(self, client: AsyncClient):
        """Test getting user with invalid token"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_user_expired_token(self, client: AsyncClient, mock_user):
        """Test getting user with expired token"""
        # Create expired token
        expiration = datetime.now(timezone.utc) - timedelta(hours=1)
        payload = {
            "sub": str(mock_user.id),
            "tenant_id": str(mock_user.tenant_id),
            "exp": expiration,
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        }
        expired_token = jwt.encode(
            payload, settings.jwt_secret, algorithm=settings.jwt_algorithm
        )

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401


class TestLogout:
    """Tests for POST /api/v1/auth/logout"""

    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient):
        """Test successful logout"""
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert "Logged out successfully" in response.json()["message"]


class TestTokenCreation:
    """Tests for JWT token creation"""

    def test_create_access_token(self, mock_user):
        """Test token creation with valid user"""
        from app.routers.auth import create_access_token

        token, expires_in = create_access_token(
            str(mock_user.id), str(mock_user.tenant_id), settings
        )

        assert isinstance(token, str)
        assert expires_in == settings.jwt_expiration_hours * 3600

        # Decode and verify token
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        assert payload["sub"] == str(mock_user.id)
        assert payload["tenant_id"] == str(mock_user.tenant_id)
        assert "exp" in payload
        assert "iat" in payload

