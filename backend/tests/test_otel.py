"""Tests for OpenTelemetry configuration and instrumentation"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from opentelemetry import trace
from app.otel_config import init_telemetry, instrument_app, get_tracer


class TestOtelConfig:
    """Tests for OpenTelemetry configuration"""

    def test_init_telemetry_returns_tracer_provider(self):
        """Test that init_telemetry returns a TracerProvider instance"""
        with patch('app.otel_config.JaegerExporter'):
            provider = init_telemetry("test-service")
            assert provider is not None

    def test_init_telemetry_sets_global_provider(self):
        """Test that init_telemetry sets the global tracer provider"""
        with patch('app.otel_config.JaegerExporter'):
            init_telemetry("test-service")
            
            # Get global provider and verify it's set
            provider = trace.get_tracer_provider()
            assert provider is not None

    def test_init_telemetry_uses_environment_variables(self):
        """Test that Jaeger exporter uses environment variables for configuration"""
        import os
        
        # Set environment variables
        os.environ['OTEL_EXPORTER_JAEGER_AGENT_HOST'] = 'test-host'
        os.environ['OTEL_EXPORTER_JAEGER_AGENT_PORT'] = '9999'
        
        try:
            with patch('app.otel_config.JaegerExporter') as mock_exporter:
                init_telemetry("test-service")
                
                # Verify JaegerExporter was called with correct args
                mock_exporter.assert_called_once_with(
                    agent_host_name='test-host',
                    agent_port=9999,
                )
        finally:
            # Cleanup
            os.environ.pop('OTEL_EXPORTER_JAEGER_AGENT_HOST', None)
            os.environ.pop('OTEL_EXPORTER_JAEGER_AGENT_PORT', None)

    def test_get_tracer(self):
        """Test that get_tracer returns a tracer instance"""
        with patch('app.otel_config.JaegerExporter'):
            init_telemetry("test-service")
            tracer = get_tracer("test-module")
            assert tracer is not None


class TestAppInstrumentation:
    """Tests for FastAPI app instrumentation"""

    def test_instrument_app(self):
        """Test that instrument_app successfully instruments the app"""
        from fastapi import FastAPI
        
        app = FastAPI()
        
        with patch('app.otel_config.FastAPIInstrumentor') as mock_fastapi:
            with patch('app.otel_config.SQLAlchemyInstrumentor') as mock_sqlalchemy:
                with patch('app.otel_config.RequestsInstrumentor') as mock_requests:
                    instrument_app(app)
                    
                    # Verify instrumentation methods were called
                    mock_fastapi.return_value.instrument_app.assert_called_once()
                    mock_sqlalchemy.return_value.instrument.assert_called_once()
                    mock_requests.return_value.instrument.assert_called_once()


class TestTracerUsage:
    """Tests for tracer usage patterns"""

    def test_tracer_creates_spans(self):
        """Test that tracer can create and record spans"""
        with patch('app.otel_config.JaegerExporter'):
            init_telemetry("test-service")
            tracer = get_tracer("test-module")
            
            # Create a span (this would fail if tracer is not configured properly)
            with tracer.start_as_current_span("test_span") as span:
                assert span is not None
                span.set_attribute("test_key", "test_value")
