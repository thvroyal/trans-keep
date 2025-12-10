"""Tests for translation status endpoint"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status

from app.models.translation import TranslationStatus
from app.routers.status import _calculate_eta, _calculate_progress


class TestStatusEndpoint:
    """Test GET /api/v1/status/{job_id} endpoint"""

    @pytest.mark.asyncio
    async def test_get_status_success(self, test_client, mock_db_session, mock_user, mock_translation):
        """Test successful status retrieval"""
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_translation
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Mock Redis cache (no progress data)
        with patch("app.routers.status.get_redis_client") as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client
            
            with patch("app.routers.status.Cache") as mock_cache_class:
                mock_cache = AsyncMock()
                mock_cache.get_json.return_value = None
                mock_cache_class.return_value = mock_cache
                
                response = test_client.get(
                    f"/api/v1/status/{mock_translation.id}",
                    headers={"Authorization": "Bearer fake_token"},
                )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["job_id"] == str(mock_translation.id)
        assert data["status"] == mock_translation.status.value
        assert "progress" in data

    @pytest.mark.asyncio
    async def test_get_status_not_found(self, test_client, mock_db_session, mock_user):
        """Test status for non-existent job"""
        job_id = str(uuid4())
        
        # Mock database query returning None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        response = test_client.get(
            f"/api/v1/status/{job_id}",
            headers={"Authorization": "Bearer fake_token"},
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_status_invalid_uuid(self, test_client, mock_user):
        """Test status with invalid job ID format"""
        response = test_client.get(
            "/api/v1/status/invalid-uuid",
            headers={"Authorization": "Bearer fake_token"},
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_get_status_unauthorized(self, test_client):
        """Test status without authentication"""
        job_id = str(uuid4())
        
        response = test_client.get(f"/api/v1/status/{job_id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_status_wrong_user(self, test_client, mock_db_session, mock_user, mock_translation):
        """Test status for job owned by different user"""
        # Change translation user_id to different user
        mock_translation.user_id = uuid4()
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_translation
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        response = test_client.get(
            f"/api/v1/status/{mock_translation.id}",
            headers={"Authorization": "Bearer fake_token"},
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_get_status_with_progress_data(self, test_client, mock_db_session, mock_user, mock_translation):
        """Test status with Redis progress data"""
        # Set translation to translating status
        mock_translation.status = TranslationStatus.TRANSLATING
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_translation
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        # Mock Redis cache with progress data
        progress_data = {
            "stage": "translation",
            "translated_blocks": 45,
            "total_blocks": 100,
            "progress_percent": 45,
        }
        
        with patch("app.routers.status.get_redis_client") as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client
            
            with patch("app.routers.status.Cache") as mock_cache_class:
                mock_cache = AsyncMock()
                mock_cache.get_json.return_value = progress_data
                mock_cache_class.return_value = mock_cache
                
                response = test_client.get(
                    f"/api/v1/status/{mock_translation.id}",
                    headers={"Authorization": "Bearer fake_token"},
                )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["translated_blocks"] == 45
        assert data["total_blocks"] == 100


class TestProgressCalculation:
    """Test progress calculation logic"""

    def test_calculate_progress_pending(self):
        """Test progress for pending status"""
        progress = _calculate_progress(TranslationStatus.PENDING, None)
        assert progress == 0

    def test_calculate_progress_extracting(self):
        """Test progress for extracting status"""
        progress_data = {
            "current_page": 3,
            "total_pages": 10,
        }
        progress = _calculate_progress(TranslationStatus.EXTRACTING, progress_data)
        assert progress == 9  # (3/10) * 30

    def test_calculate_progress_extracting_no_data(self):
        """Test progress for extracting with no data"""
        progress = _calculate_progress(TranslationStatus.EXTRACTING, None)
        assert progress == 15  # Default mid-extraction

    def test_calculate_progress_translating(self):
        """Test progress for translating status"""
        progress_data = {
            "translated_blocks": 50,
            "total_blocks": 100,
        }
        progress = _calculate_progress(TranslationStatus.TRANSLATING, progress_data)
        # (50/100) * 65 + 30 = 32.5 + 30 = 62.5 -> 62
        assert progress == 62

    def test_calculate_progress_translating_no_data(self):
        """Test progress for translating with no data"""
        progress = _calculate_progress(TranslationStatus.TRANSLATING, None)
        assert progress == 60  # Default mid-translation

    def test_calculate_progress_completed(self):
        """Test progress for completed status"""
        progress = _calculate_progress(TranslationStatus.COMPLETED, None)
        assert progress == 100

    def test_calculate_progress_failed(self):
        """Test progress for failed status"""
        progress_data = {"progress_percent": 45}
        progress = _calculate_progress(TranslationStatus.FAILED, progress_data)
        assert progress == 45  # Last known progress

    def test_calculate_progress_failed_no_data(self):
        """Test progress for failed with no data"""
        progress = _calculate_progress(TranslationStatus.FAILED, None)
        assert progress == 0


class TestETACalculation:
    """Test ETA calculation logic"""

    def test_calculate_eta_no_progress(self):
        """Test ETA with 0% progress"""
        created = datetime.utcnow()
        started = datetime.utcnow()
        eta = _calculate_eta(created, started, 0)
        assert eta is None

    def test_calculate_eta_completed(self):
        """Test ETA with 100% progress"""
        created = datetime.utcnow()
        started = datetime.utcnow()
        eta = _calculate_eta(created, started, 100)
        assert eta is None

    def test_calculate_eta_no_start_time(self):
        """Test ETA without start time"""
        created = datetime.utcnow()
        eta = _calculate_eta(created, None, 50)
        assert eta is None

    def test_calculate_eta_mid_progress(self):
        """Test ETA at 50% progress"""
        created = datetime.utcnow()
        started = datetime.utcnow() - timedelta(seconds=60)  # Started 60 seconds ago
        eta = _calculate_eta(created, started, 50)
        # At 50%, estimated total = 60 / 0.5 = 120 seconds
        # ETA = 120 - 60 = 60 seconds
        assert eta == 60

    def test_calculate_eta_early_progress(self):
        """Test ETA at 10% progress"""
        created = datetime.utcnow()
        started = datetime.utcnow() - timedelta(seconds=30)
        eta = _calculate_eta(created, started, 10)
        # At 10%, estimated total = 30 / 0.1 = 300 seconds
        # ETA = 300 - 30 = 270 seconds
        assert eta == 270

    def test_calculate_eta_clamped(self):
        """Test ETA is clamped to reasonable range"""
        created = datetime.utcnow()
        started = datetime.utcnow() - timedelta(seconds=3600)  # 1 hour ago
        eta = _calculate_eta(created, started, 1)
        # Would calculate huge ETA, but should be clamped to 3600
        assert eta == 3600

    def test_calculate_eta_negative_clamped(self):
        """Test negative ETA is clamped to 0"""
        created = datetime.utcnow()
        started = datetime.utcnow() - timedelta(seconds=120)
        eta = _calculate_eta(created, started, 99)
        # Should be positive but close to 0
        assert eta >= 0

