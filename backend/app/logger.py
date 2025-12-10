"""Structured JSON logging with trace context for TransKeep backend"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from opentelemetry import trace
from opentelemetry.trace import get_current_span


class JSONFormatter(logging.Formatter):
    """Custom logging formatter that outputs structured JSON logs with trace context"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON with trace and span IDs.
        
        Args:
            record: LogRecord to format
        
        Returns:
            JSON-formatted log string
        """
        # Get current trace and span context
        span = get_current_span()
        trace_id = None
        span_id = None
        
        if span and span.is_recording():
            trace_id = format(span.get_span_context().trace_id, '032x')
            span_id = format(span.get_span_context().span_id, '016x')
        
        # Build log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "transkeep-backend",
            "message": record.getMessage(),
        }
        
        # Add trace context if available
        if trace_id:
            log_entry["trace_id"] = trace_id
        if span_id:
            log_entry["span_id"] = span_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields from the record
        if hasattr(record, "extra_fields"):
            log_entry["context"] = record.extra_fields
        
        return json.dumps(log_entry)


class StructuredLogger:
    """Structured logging utility with trace context injection"""
    
    def __init__(self, name: str = "transkeep"):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
        self._setup_handler()
    
    def _setup_handler(self) -> None:
        """Configure logging handler with JSON formatter"""
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create stdout handler with JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
        
        # Set default level to INFO
        self.logger.setLevel(logging.INFO)
    
    def debug(self, message: str, **context: Any) -> None:
        """Log debug message with optional context"""
        self._log(logging.DEBUG, message, context)
    
    def info(self, message: str, **context: Any) -> None:
        """Log info message with optional context"""
        self._log(logging.INFO, message, context)
    
    def warning(self, message: str, **context: Any) -> None:
        """Log warning message with optional context"""
        self._log(logging.WARNING, message, context)
    
    def error(self, message: str, exc: Optional[Exception] = None, **context: Any) -> None:
        """Log error message with optional exception and context"""
        if exc:
            self._log(logging.ERROR, message, context, exc_info=exc)
        else:
            self._log(logging.ERROR, message, context)
    
    def _log(
        self,
        level: int,
        message: str,
        context: Dict[str, Any],
        exc_info: Optional[Exception] = None,
    ) -> None:
        """
        Internal logging method that attaches context to record.
        
        Args:
            level: Logging level
            message: Log message
            context: Additional context fields
            exc_info: Optional exception info
        """
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "(unknown file)",
            0,
            message,
            (),
            exc_info,
        )
        
        # Attach context fields to record
        if context:
            record.extra_fields = context
        
        self.logger.handle(record)


# Global logger instance
_logger = StructuredLogger()


# Convenience functions for module-level usage
def debug(message: str, **context: Any) -> None:
    """Log debug message"""
    _logger.debug(message, **context)


def info(message: str, **context: Any) -> None:
    """Log info message"""
    _logger.info(message, **context)


def warning(message: str, **context: Any) -> None:
    """Log warning message"""
    _logger.warning(message, **context)


def error(message: str, exc: Optional[Exception] = None, **context: Any) -> None:
    """Log error message"""
    _logger.error(message, exc=exc, **context)


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance for a specific module.
    
    Args:
        name: Module name or identifier
    
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)



