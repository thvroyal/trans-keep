# 9. Monitoring & Observability

## 9.1 Key Metrics to Track

**Business Metrics:**
- Daily active users (DAU)
- Total documents translated
- Freemium to paid conversion rate
- Average translation time
- User satisfaction (NPS)

**Technical Metrics:**
- API response times (p50, p95, p99)
- Error rates (by endpoint, by error type)
- Job processing time (extract, translate, tone, reconstruct)
- Worker queue depth (Celery pending jobs)
- S3 upload/download bandwidth
- Database connection pool usage

**System Metrics:**
- CPU/memory utilization (ECS tasks)
- Database disk usage
- Redis memory usage
- Network I/O

## 9.2 Logging Strategy (OpenTelemetry Protocol)

**OpenTelemetry (Otel) Implementation:**
- Use Otel protocol for vendor-agnostic observability
- Backend: `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp`
- Workers: `opentelemetry-instrumentation-celery`
- Frontend: `@opentelemetry/api` + exporters
- Flexibility: Switch backends (CloudWatch → Datadog → Jaeger) without code changes

**Installation:**
```bash
# Backend
pip install opentelemetry-api opentelemetry-sdk
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-exporter-otlp
pip install opentelemetry-instrumentation-sqlalchemy
pip install opentelemetry-instrumentation-requests

# Celery workers
pip install opentelemetry-instrumentation-celery

# Frontend
npm install @opentelemetry/api @opentelemetry/sdk-web
npm install @opentelemetry/auto-instrumentations-web
npm install @opentelemetry/exporter-trace-otlp-http
```

**Log Levels:**
- DEBUG: Development only, detailed flow
- INFO: Key milestones (user login, job started, job completed)
- WARNING: Recoverable issues (retry attempt, degraded service)
- ERROR: Problems (API failure, DB error)

**Log Structure (JSON with Otel trace/span IDs):**
```json
{
  "timestamp": "2025-11-14T10:30:45Z",
  "level": "INFO",
  "service": "backend",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "user_id": "uuid",
  "tenant_id": "uuid",
  "job_id": "uuid",
  "action": "translation_started",
  "duration_ms": 125,
  "details": {
    "file_size_mb": 2.4,
    "language_pair": "en_ja",
    "page_count": 45
  }
}
```

**Otel Exporter Configuration:**
```python
# backend/app/config.py
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces"  # Local: Jaeger
    # For AWS: endpoint="http://otel-collector.local:4318/v1/traces"
)

trace_provider = TracerProvider()
trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
```

**CloudWatch Integration (via Otel Collector):**
- Deploy Otel Collector in ECS
- Collector receives traces via OTLP protocol
- Exporter sends to CloudWatch Logs + CloudWatch Metrics + X-Ray
- Alarms: Error rate > 5%, Response time p99 > 5s, Queue depth > 100
- Vendor flexibility: Can also export to Datadog, New Relic, etc.

---
