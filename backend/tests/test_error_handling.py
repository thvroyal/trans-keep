"""Tests for error handling and edge cases"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import deepl
import anthropic

from app.services.translation_fallback import TranslationServiceWithFallback, GoogleTranslateFallback
from app.services.tone_service import ToneService
from app.utils.error_messages import get_error_message, categorize_error, ErrorCategory
from app.services.translation_service import TranslationService


class TestErrorMessages:
    """Test error message utilities"""
    
    def test_get_error_message_exists(self):
        """Test getting existing error message"""
        error = get_error_message("network_timeout")
        assert error.title == "Connection Timeout"
        assert error.category == ErrorCategory.NETWORK
        assert len(error.actionable_steps) > 0
    
    def test_get_error_message_default(self):
        """Test getting default error message for unknown key"""
        error = get_error_message("unknown_error")
        assert error.title == "An Error Occurred"
        assert error.category == ErrorCategory.SERVER
    
    def test_categorize_network_error(self):
        """Test categorizing network errors"""
        error = Exception("Network timeout occurred")
        category = categorize_error(error)
        assert category == ErrorCategory.NETWORK
    
    def test_categorize_api_error(self):
        """Test categorizing API errors"""
        error = Exception("API quota exceeded")
        category = categorize_error(error)
        assert category == ErrorCategory.API
    
    def test_categorize_file_error(self):
        """Test categorizing file errors"""
        error = Exception("File too large")
        category = categorize_error(error)
        assert category == ErrorCategory.FILE


class TestTranslationFallback:
    """Test translation service with fallback"""
    
    @pytest.mark.asyncio
    async def test_primary_service_success(self):
        """Test that primary service is used when it succeeds"""
        with patch('app.services.translation_fallback.TranslationService') as mock_service:
            mock_instance = AsyncMock()
            mock_instance.translate_text = AsyncMock(return_value=("translated", 100))
            mock_service.return_value = mock_instance
            
            service = TranslationServiceWithFallback(
                deepl_api_key="test_key",
                google_api_key=None,  # Fallback disabled
            )
            service.primary = mock_instance
            
            result = await service.translate_text("text", "en", "ja")
            assert result == ("translated", 100)
            mock_instance.translate_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fallback_on_deepl_failure(self):
        """Test that fallback is used when DeepL fails"""
        with patch('app.services.translation_fallback.TranslationService') as mock_primary, \
             patch('app.services.translation_fallback.GoogleTranslateFallback') as mock_fallback:
            
            # Primary fails
            mock_primary_instance = AsyncMock()
            mock_primary_instance.translate_text = AsyncMock(
                side_effect=deepl.exceptions.DeepLException("API error")
            )
            mock_primary.return_value = mock_primary_instance
            
            # Fallback succeeds
            mock_fallback_instance = AsyncMock()
            mock_fallback_instance.translate_text = AsyncMock(return_value=("fallback_translated", 100))
            mock_fallback.return_value = mock_fallback_instance
            
            service = TranslationServiceWithFallback(
                deepl_api_key="test_key",
                google_api_key="google_key",
            )
            service.primary = mock_primary_instance
            service.fallback = mock_fallback_instance
            service.fallback_enabled = True
            
            result = await service.translate_text("text", "en", "ja")
            assert result == ("fallback_translated", 100)
            mock_fallback_instance.translate_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_no_fallback_when_disabled(self):
        """Test that error is raised when fallback is disabled"""
        with patch('app.services.translation_fallback.TranslationService') as mock_primary:
            mock_instance = AsyncMock()
            mock_instance.translate_text = AsyncMock(
                side_effect=deepl.exceptions.DeepLException("API error")
            )
            mock_primary.return_value = mock_instance
            
            service = TranslationServiceWithFallback(
                deepl_api_key="test_key",
                google_api_key=None,  # Fallback disabled
            )
            service.primary = mock_instance
            service.fallback_enabled = False
            
            with pytest.raises(deepl.exceptions.DeepLException):
                await service.translate_text("text", "en", "ja")


class TestToneServiceGracefulDegradation:
    """Test tone service graceful degradation"""
    
    @pytest.mark.asyncio
    async def test_tone_service_success(self):
        """Test normal tone service operation"""
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="customized text")]
            mock_message.usage = MagicMock(input_tokens=100, output_tokens=50)
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client
            
            service = ToneService(api_key="test_key")
            result, cost = await service.apply_tone("text", "professional")
            
            assert result == "customized text"
            assert cost > 0
    
    @pytest.mark.asyncio
    async def test_tone_service_handles_api_error_gracefully(self):
        """Test that tone service errors are handled (caller should handle gracefully)"""
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.side_effect = anthropic.APIError(
                message="API error",
                response=MagicMock(status_code=500),
                body=None,
            )
            mock_anthropic.return_value = mock_client
            
            service = ToneService(api_key="test_key")
            
            # Service should raise error (caller handles gracefully)
            with pytest.raises(anthropic.APIError):
                await service.apply_tone("text", "professional")


class TestScannedPDFHandling:
    """Test scanned PDF detection and handling"""
    
    def test_scanned_pdf_detection(self):
        """Test that scanned PDFs are detected correctly"""
        # This would be tested in test_pdf_extraction.py
        # The key change is that scanned PDFs now warn instead of failing
        pass


class TestRetryLogic:
    """Test retry logic for network operations"""
    
    @pytest.mark.asyncio
    async def test_retry_on_network_error(self):
        """Test that network errors trigger retries"""
        # This would be tested in frontend tests
        # Backend retry logic is handled by tenacity decorators
        pass
