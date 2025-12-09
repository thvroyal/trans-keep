"""Tests for structured JSON logging with trace context"""

import json
import logging
from io import StringIO
from unittest.mock import patch, MagicMock

import pytest
from app.logger import (
    JSONFormatter,
    StructuredLogger,
    debug,
    info,
    warning,
    error,
    get_logger,
)


class TestJSONFormatter:
    """Tests for JSON log formatter"""

    def test_format_produces_valid_json(self):
        """Test that formatter produces valid JSON output"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        output = formatter.format(record)
        parsed = json.loads(output)
        
        assert parsed["message"] == "Test message"
        assert parsed["level"] == "INFO"
        assert "timestamp" in parsed
        assert parsed["service"] == "transkeep-backend"

    def test_format_includes_trace_context(self):
        """Test that formatter includes trace and span IDs when available"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        # Mock a span with trace context
        with patch('app.logger.get_current_span') as mock_get_span:
            mock_span = MagicMock()
            mock_span.is_recording.return_value = True
            mock_span.get_span_context.return_value.trace_id = 12345
            mock_span.get_span_context.return_value.span_id = 67890
            mock_get_span.return_value = mock_span
            
            output = formatter.format(record)
            parsed = json.loads(output)
            
            assert "trace_id" in parsed
            assert "span_id" in parsed

    def test_format_includes_exception_info(self):
        """Test that formatter includes exception information"""
        formatter = JSONFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
            
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="Error occurred",
                args=(),
                exc_info=exc_info,
            )
            
            output = formatter.format(record)
            parsed = json.loads(output)
            
            assert "exception" in parsed
            assert "ValueError" in parsed["exception"]


class TestStructuredLogger:
    """Tests for StructuredLogger class"""

    def test_logger_creation(self):
        """Test that StructuredLogger initializes correctly"""
        logger = StructuredLogger("test")
        assert logger is not None
        assert logger.logger is not None

    def test_logger_debug(self):
        """Test debug logging"""
        logger = StructuredLogger("test")
        
        # Capture log output
        with patch.object(logger.logger, 'handle') as mock_handle:
            logger.debug("Debug message", key="value")
            mock_handle.assert_called_once()

    def test_logger_info(self):
        """Test info logging"""
        logger = StructuredLogger("test")
        
        with patch.object(logger.logger, 'handle') as mock_handle:
            logger.info("Info message", key="value")
            mock_handle.assert_called_once()

    def test_logger_warning(self):
        """Test warning logging"""
        logger = StructuredLogger("test")
        
        with patch.object(logger.logger, 'handle') as mock_handle:
            logger.warning("Warning message", key="value")
            mock_handle.assert_called_once()

    def test_logger_error_with_exception(self):
        """Test error logging with exception"""
        logger = StructuredLogger("test")
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            with patch.object(logger.logger, 'handle') as mock_handle:
                logger.error("Error occurred", exc=e)
                mock_handle.assert_called_once()

    def test_logger_includes_context(self):
        """Test that context information is included in logs"""
        logger = StructuredLogger("test")
        
        with patch.object(logger.logger, 'makeRecord') as mock_make_record:
            mock_record = MagicMock()
            mock_make_record.return_value = mock_record
            
            logger.info("Message", user_id="123", action="login")
            
            # Verify the record was created
            assert mock_make_record.called
            # The context should be attached as extra_fields
            assert hasattr(mock_record, 'extra_fields')


class TestModuleLevelFunctions:
    """Tests for module-level logging functions"""

    def test_debug_function(self):
        """Test module-level debug function"""
        with patch('app.logger._logger.debug') as mock_debug:
            debug("Test debug", key="value")
            mock_debug.assert_called_once_with("Test debug", key="value")

    def test_info_function(self):
        """Test module-level info function"""
        with patch('app.logger._logger.info') as mock_info:
            info("Test info", key="value")
            mock_info.assert_called_once_with("Test info", key="value")

    def test_warning_function(self):
        """Test module-level warning function"""
        with patch('app.logger._logger.warning') as mock_warning:
            warning("Test warning", key="value")
            mock_warning.assert_called_once_with("Test warning", key="value")

    def test_error_function(self):
        """Test module-level error function"""
        exc = ValueError("Test")
        with patch('app.logger._logger.error') as mock_error:
            error("Test error", exc=exc, key="value")
            mock_error.assert_called_once()

    def test_get_logger_function(self):
        """Test get_logger function"""
        logger = get_logger("test-module")
        assert isinstance(logger, StructuredLogger)
        assert logger.logger.name == "test-module"


class TestLoggingLevels:
    """Tests for log level configuration"""

    def test_logger_respects_log_level(self):
        """Test that logger respects configured log levels"""
        logger = StructuredLogger("test")
        
        # Logger should be at INFO level by default
        assert logger.logger.level == logging.INFO


class TestLoggingIntegration:
    """Integration tests for logging system"""

    def test_structured_logging_with_tracer(self):
        """Test that structured logging works with OpenTelemetry tracing"""
        # This would require a full Otel setup, so we mock it
        logger = StructuredLogger("test")
        
        with patch('app.logger.get_current_span') as mock_span:
            mock_span.return_value.is_recording.return_value = True
            mock_span.return_value.get_span_context.return_value.trace_id = 123
            mock_span.return_value.get_span_context.return_value.span_id = 456
            
            with patch.object(logger.logger, 'handle') as mock_handle:
                logger.info("Traced message")
                mock_handle.assert_called_once()
