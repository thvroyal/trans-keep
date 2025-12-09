"""Tests for Celery task queue"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.celery_app import celery_app, health_check


class TestCeleryConfiguration:
    """Test Celery configuration"""

    def test_celery_app_exists(self):
        """Test that Celery app is properly initialized"""
        assert celery_app is not None
        assert celery_app.main == "transkeep"

    def test_celery_broker_configured(self):
        """Test that Redis broker is configured"""
        assert "redis://" in celery_app.conf.broker_url

    def test_celery_backend_configured(self):
        """Test that result backend is configured"""
        assert "redis://" in celery_app.conf.result_backend

    def test_celery_task_serializer(self):
        """Test that JSON serializer is configured"""
        assert celery_app.conf.task_serializer == "json"
        assert "json" in celery_app.conf.accept_content

    def test_celery_task_routes(self):
        """Test that task routes are configured"""
        routes = celery_app.conf.task_routes
        assert routes is not None
        assert "app.tasks.extract_pdf.*" in routes
        assert "app.tasks.translate_blocks.*" in routes

    def test_celery_task_timeout_configured(self):
        """Test that task timeouts are set"""
        assert celery_app.conf.task_soft_time_limit == 600
        assert celery_app.conf.task_time_limit == 720

    def test_health_check_task(self):
        """Test health check task"""
        result = health_check()
        assert result["status"] == "healthy"
        assert "message" in result


class TestCeleryTasks:
    """Test Celery tasks registration"""

    def test_extract_pdf_task_registered(self):
        """Test that extract_pdf task is registered"""
        assert "extract_pdf" in celery_app.tasks

    def test_translate_blocks_task_registered(self):
        """Test that translate_blocks task is registered"""
        assert "translate_blocks" in celery_app.tasks

    def test_process_translation_pipeline_registered(self):
        """Test that orchestrator task is registered"""
        assert "process_translation_pipeline" in celery_app.tasks


@pytest.mark.asyncio
class TestTaskOrchestrator:
    """Test task orchestration"""

    @patch("app.tasks.orchestrator.extract_pdf_sync")
    @patch("app.tasks.orchestrator.translate_blocks_sync")
    async def test_pipeline_success(self, mock_translate, mock_extract):
        """Test successful pipeline execution"""
        # Mock successful extraction
        mock_extract.return_value = {
            "success": True,
            "blocks": 10,
            "pages": 5,
        }
        
        # Mock successful translation
        mock_translate.return_value = {
            "success": True,
            "translated_blocks": 10,
            "cost_usd": 0.05,
        }
        
        from app.tasks.orchestrator import _run_pipeline_async
        
        result = await _run_pipeline_async("test-job-id")
        
        assert result["success"] is True
        assert "extraction" in result
        assert "translation" in result

    @patch("app.tasks.orchestrator.extract_pdf_sync")
    async def test_pipeline_extraction_failure(self, mock_extract):
        """Test pipeline handles extraction failure"""
        # Mock extraction failure
        mock_extract.return_value = {
            "success": False,
            "error": "PDF corrupted",
        }
        
        from app.tasks.orchestrator import _run_pipeline_async
        
        with pytest.raises(Exception, match="Extraction failed"):
            await _run_pipeline_async("test-job-id")

    @patch("app.tasks.orchestrator.extract_pdf_sync")
    @patch("app.tasks.orchestrator.translate_blocks_sync")
    async def test_pipeline_translation_failure(self, mock_translate, mock_extract):
        """Test pipeline handles translation failure"""
        # Mock successful extraction
        mock_extract.return_value = {
            "success": True,
            "blocks": 10,
        }
        
        # Mock translation failure
        mock_translate.return_value = {
            "success": False,
            "error": "API quota exceeded",
        }
        
        from app.tasks.orchestrator import _run_pipeline_async
        
        with pytest.raises(Exception, match="Translation failed"):
            await _run_pipeline_async("test-job-id")


class TestTaskTrigger:
    """Test task triggering"""

    @patch("app.tasks.orchestrator.process_translation_pipeline.delay")
    def test_trigger_translation_pipeline(self, mock_delay):
        """Test triggering translation pipeline"""
        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_delay.return_value = mock_task
        
        from app.tasks.orchestrator import trigger_translation_pipeline
        
        task_id = trigger_translation_pipeline("job-456")
        
        assert task_id == "task-123"
        mock_delay.assert_called_once_with("job-456")
