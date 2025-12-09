"""Tracing middleware for OpenTelemetry span management"""

from fastapi import Request
from opentelemetry import trace, context
from opentelemetry.trace import Status, StatusCode


class TracingMiddleware:
    """
    Middleware for managing OpenTelemetry trace context across requests.
    
    This middleware ensures trace context is propagated and available
    throughout the request lifecycle.
    """
    
    def __init__(self, app):
        """
        Initialize tracing middleware.
        
        Args:
            app: FastAPI application instance
        """
        self.app = app
        self.tracer = trace.get_tracer(__name__)
    
    async def __call__(self, request: Request, call_next):
        """
        Process request with trace context management.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
        
        Returns:
            Response with trace context
        """
        # Extract trace context from request headers if present
        ctx = trace.set_span_in_context(trace.get_current_span())
        
        # Create a span for this request
        with self.tracer.start_as_current_span(
            f"{request.method} {request.url.path}"
        ) as span:
            # Add request attributes to span
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.target", request.url.path)
            
            try:
                # Process request through middleware chain
                response = await call_next(request)
                
                # Add response status to span
                span.set_attribute("http.status_code", response.status_code)
                
                # Set span status based on HTTP status code
                if 400 <= response.status_code < 500:
                    span.set_status(Status(StatusCode.UNSET))
                elif response.status_code >= 500:
                    span.set_status(Status(StatusCode.ERROR))
                else:
                    span.set_status(Status(StatusCode.OK))
                
                return response
            
            except Exception as exc:
                # Record exception in span
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR))
                raise
