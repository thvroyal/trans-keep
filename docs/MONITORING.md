# TransKeep Monitoring & Observability Guide

**Last Updated:** December 9, 2025  
**Status:** Initial Implementation Complete

---

## Overview

TransKeep uses **OpenTelemetry protocol** for vendor-agnostic distributed tracing and observability. During development, traces are exported to **Jaeger** for visualization. The system supports seamless migration to production observability backends (CloudWatch, Datadog, etc.) without code changes.

---

## Architecture

```
┌──────────────────┐                    ┌──────────────────┐
│   Frontend       │                    │   Backend        │
│   (React)        │                    │   (FastAPI)      │
│                  │                    │                  │
│  Otel Web SDK    │───HTTP (OTLP)──→  │  Otel SDK        │
│  w/auto-instr.   │                    │  w/auto-instr.   │
└──────┬───────────┘                    └──────┬───────────┘
       │                                       │
       │          Both send traces via         │
       │          OTLP HTTP protocol           │
       │                                       │
       └────────────────┬─────────────────────┘
                        │
                        ↓
                   ┌──────────────┐
                   │  Jaeger      │
                   │  Collector   │
                   │              │
                   │ :4318 (HTTP) │
                   │ :6831 (UDP)  │
                   └──────┬───────┘
                          │
                          ↓
                   ┌──────────────┐
                   │  Jaeger UI   │
                   │              │
                   │ :16686       │
                   │  localhost   │
                   └──────────────┘
```

---

## Getting Started

### 1. Start Services with Docker Compose

```bash
docker-compose up --build
```

This starts:
- **Frontend** (React): http://localhost:3000
- **Backend** (FastAPI): http://localhost:8000
- **Jaeger UI**: http://localhost:16686
- **Database** (PostgreSQL): localhost:5432
- **Cache** (Redis): localhost:6379

### 2. Access Jaeger UI

Open http://localhost:16686 in your browser to view distributed traces.

### 3. Make Requests to Generate Traces

```bash
# Simple health check that generates a trace
curl http://localhost:8000/health

# Visit frontend at http://localhost:3000
# Any user interaction generates frontend traces
```

---

## Viewing Traces

### Trace Search

1. Open **Jaeger UI** at http://localhost:16686
2. Select service from dropdown:
   - `transkeep-backend` - Backend API traces
   - `transkeep-frontend` - Frontend application traces
3. Click **Find Traces** to view recent traces

### Trace Details

Click on any trace to see:
- **Timeline**: Sequential operations with duration
- **Waterfall**: Hierarchical span relationships
- **Span Tags**: Attributes (URL, method, status code, etc.)
- **Logs**: Structured logs within the span
- **Errors**: Exception information and stack traces

### Performance Analysis

In the **Service Graph** view:
- See real-time service dependencies
- Identify bottlenecks and slow operations
- Monitor error rates across services

---

## Instrumentation Details

### Backend (FastAPI)

**What's automatically traced:**
- ✅ All HTTP endpoints (method, URL, status code)
- ✅ Request/response lifecycle
- ✅ Database queries (SQLAlchemy)
- ✅ HTTP client calls (requests library)
- ✅ Exceptions and error conditions

**Configuration:** `backend/app/otel_config.py`

```python
# Initialize Otel on app startup
init_telemetry("transkeep-backend")
instrument_app(app)  # Instruments FastAPI and libraries
```

**Custom Instrumentation:**

```python
from app.otel_config import get_tracer

tracer = get_tracer("my_module")

with tracer.start_as_current_span("operation_name") as span:
    span.set_attribute("user_id", user.id)
    span.set_attribute("file_size", file_size)
    # ... perform operation ...
```

### Frontend (React)

**What's automatically traced:**
- ✅ HTTP requests (fetch, axios)
- ✅ Navigation events (React Router)
- ✅ Component lifecycle (with instrumentation)
- ✅ Errors and console exceptions

**Configuration:** `frontend/src/otelConfig.ts`

```typescript
// Initialize in main.tsx before rendering
initTelemetry('transkeep-frontend', 'http://localhost:4318/v1/traces')
```

---

## Structured Logging

### Backend Log Format

All backend logs are **structured JSON** with trace context:

```json
{
  "timestamp": "2025-12-09T10:30:45.123Z",
  "level": "INFO",
  "service": "transkeep-backend",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "message": "User uploaded file",
  "context": {
    "user_id": "user-123",
    "file_size": 5242880,
    "file_type": "pdf"
  }
}
```

### Using Structured Logger

```python
from app.logger import info, error, get_logger

# Simple info log
info("User signed in", user_id=user.id)

# Error with exception
error("PDF extraction failed", exc=e, file_id=file.id)

# Get module-specific logger
logger = get_logger("translation_module")
logger.info("Translation started", language="es", file_id=file.id)
```

### Log Levels

| Level | When to Use | Example |
|-------|-----------|---------|
| **DEBUG** | Detailed development info (disabled in prod) | Loop iterations, variable values |
| **INFO** | Important milestones (startup, user actions) | "User signed in", "File uploaded" |
| **WARNING** | Recoverable issues (retries, rate limits) | "Redis connection lost, retrying..." |
| **ERROR** | Failures requiring attention | Exceptions, failed API calls |

---

## Key Metrics to Monitor

### Business Metrics
- **Daily Active Users (DAU)** - User engagement
- **Documents Translated** - Core product metric
- **Translation Success Rate** - Quality metric
- **Average Translation Time** - Performance metric

### Technical Metrics
- **Request Latency** - API response time (p50, p95, p99)
- **Error Rate** - % of failed requests by endpoint
- **Database Query Time** - Average query duration
- **Cache Hit Rate** - Redis effectiveness

### System Metrics
- **CPU Usage** - Container resource utilization
- **Memory Usage** - Heap memory consumption
- **Active Connections** - Database and Redis connections
- **Queue Depth** - Celery job queue length

---

## Trace Context Propagation

Trace IDs automatically flow between frontend and backend:

```
Browser Request
    ↓
Frontend creates span
  trace_id: abc123
  span_id: xyz789
    ↓
HTTP Header added:
  traceparent: 00-abc123-xyz789-01
    ↓
Backend receives request
  Extracts trace context
  Continues in same trace
    ↓
Database query
  Same trace_id
  New span_id (child)
    ↓
Backend response
  Response includes trace ID header
    ↓
Frontend logs included in same trace
```

---

## Common Use Cases

### Debugging Slow Requests

1. Open Jaeger UI → Select `transkeep-backend`
2. Search for traces with long duration: **Min Duration**: 1s
3. Click a slow trace to see timeline
4. Identify which span took longest (usually database query)
5. Optimize that operation

### Tracking User Journey

1. Get user ID from application logs
2. Jaeger UI → Add tag filter: `user_id: {user_id}`
3. View all traces for that user
4. See complete flow from login through document translation

### Monitoring API Health

1. Create alerts on:
   - **Error rate** > 5%
   - **P99 latency** > 2 seconds
   - **Service availability** < 99%
2. Use Jaeger Service Graph to visualize dependencies

---

## Production Deployment

### Switching to CloudWatch (AWS)

Replace Jaeger exporter with CloudWatch exporter:

```python
# backend/app/otel_config.py
from opentelemetry.exporter.awsxray.trace_exporter import AWSXRayExporter

exporter = AWSXRayExporter()
```

No other code changes required! OpenTelemetry handles the abstraction.

### Environment Configuration

```bash
# Development (Jaeger)
OTEL_EXPORTER_JAEGER_AGENT_HOST=localhost
OTEL_EXPORTER_JAEGER_AGENT_PORT=6831

# Production (CloudWatch)
AWS_REGION=us-east-1
OTEL_EXPORTER_AWS_REGION=us-east-1
```

---

## Troubleshooting

### Traces Not Appearing in Jaeger UI

**Problem:** Started requests but no traces in Jaeger

**Solutions:**
1. Verify Jaeger is running: `docker ps | grep jaeger`
2. Check Jaeger UI is accessible: http://localhost:16686
3. Verify backend can reach Jaeger:
   ```bash
   docker exec transkeep-backend curl http://jaeger:6831 -v
   ```
4. Check backend logs for initialization errors:
   ```bash
   docker logs transkeep-backend | grep -i otel
   ```

### Trace IDs Not in Logs

**Problem:** Logs missing `trace_id` field

**Solutions:**
1. Verify StructuredLogger is being used (not print())
2. Check that OpenTelemetry was initialized:
   ```python
   from app.otel_config import init_telemetry
   init_telemetry()  # Must call before logging
   ```
3. Use logger module functions:
   ```python
   from app import logger
   logger.info("message")  # ✓ Correct
   print("message")        # ✗ Missing trace context
   ```

### High Memory Usage

**Problem:** Backend or Jaeger using excessive memory

**Solutions:**
1. Reduce span batch processor size:
   ```python
   # Use SimpleSpanProcessor only in development
   # Use BatchSpanProcessor in production (smaller memory footprint)
   ```
2. Limit trace sampling to 50% or less:
   ```python
   from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
   sampler = TraceIdRatioBased(0.5)  # Sample 50% of traces
   ```
3. Restart services:
   ```bash
   docker-compose restart backend jaeger
   ```

---

## Best Practices

### Do's ✓
- Log at appropriate levels (INFO for milestones, DEBUG for details)
- Include relevant context in log fields (user_id, file_id, etc.)
- Use structured logging for machine-readability
- Set span attributes for important values
- Sample traces in production to manage cost/overhead

### Don'ts ✗
- Don't log sensitive data (passwords, tokens, PII)
- Don't create spans for every single operation (performance impact)
- Don't use print() for logs (no trace context)
- Don't forget to initialize Otel before using loggers
- Don't send unsampled traces to production (cost)

---

## Resources

- **OpenTelemetry Docs:** https://opentelemetry.io
- **Jaeger Documentation:** https://www.jaegertracing.io
- **FastAPI Instrumentation:** https://github.com/open-telemetry/opentelemetry-python-contrib
- **Architecture Reference:** docs/architecture.md (Section 9)

---

## Next Steps

After Epic 1 completion:
1. **Epic 2:** Add tracing to Celery workers (async job processing)
2. **Epic 3:** Enhanced logging for translation operations
3. **Epic 4:** Production observability (CloudWatch integration)

For more details, see **Architecture Documentation** (docs/architecture.md, Section 9: Logging Strategy).
