"""OpenTelemetry configuration for TransKeep backend"""

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource


def init_telemetry(service_name: str = "transkeep-backend") -> TracerProvider:
    """
    Initialize OpenTelemetry instrumentation with Jaeger exporter.
    
    Args:
        service_name: Name of the service for trace identification
    
    Returns:
        TracerProvider instance
    """
    # Get Jaeger configuration from environment
    jaeger_host = os.getenv("OTEL_EXPORTER_JAEGER_AGENT_HOST", "localhost")
    jaeger_port = int(os.getenv("OTEL_EXPORTER_JAEGER_AGENT_PORT", 6831))
    
    # Create Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_host,
        agent_port=jaeger_port,
    )
    
    # Create resource with service name
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })
    
    # Create tracer provider with resource
    tracer_provider = TracerProvider(resource=resource)
    
    # Add Jaeger exporter as batch processor
    tracer_provider.add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    
    # Set the global tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    return tracer_provider


def instrument_app(app) -> None:
    """
    Instrument FastAPI application and common libraries.
    
    Args:
        app: FastAPI application instance
    """
    # Instrument FastAPI endpoints
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument SQLAlchemy database calls
    SQLAlchemyInstrumentor().instrument()
    
    # Instrument HTTP requests
    RequestsInstrumentor().instrument()


def get_tracer(name: str = "transkeep-backend") -> trace.Tracer:
    """
    Get a tracer instance for custom instrumentation.
    
    Args:
        name: Module name or identifier for the tracer
    
    Returns:
        Tracer instance for creating custom spans
    """
    return trace.get_tracer(name)

