# Story 1.5: OpenTelemetry & Monitoring Setup

**Story Key:** 1-5-opentelemetry-monitoring  
**Epic:** 1 - Setup & Scaffolding  
**Week:** Week 1 (Dec 2-6)  
**Duration:** 1 day  
**Owner:** Backend Developer  
**Status:** ready-for-dev  

---

## Overview

Implement distributed tracing and observability using OpenTelemetry protocol. Backend logs, traces, and metrics flow to local Jaeger for development. Foundation for production CloudWatch integration.

---

## Acceptance Criteria

### AC 1.5.1: Backend Otel Instrumentation ✅
- [ ] OpenTelemetry FastAPI instrumentation installed
- [ ] Jaeger exporter configured
- [ ] All FastAPI endpoints traced
- [ ] Database queries traced
- [ ] Error traces captured

### AC 1.5.2: Frontend Otel Instrumentation ✅
- [ ] OpenTelemetry Web SDK installed
- [ ] HTTP request tracing working
- [ ] Error tracing captured
- [ ] Traces sent to Jaeger collector

### AC 1.5.3: Jaeger Integration ✅
- [ ] Jaeger running in docker-compose
- [ ] Traces visible in Jaeger UI (localhost:16686)
- [ ] Trace IDs logged in application logs
- [ ] Requests tracked end-to-end (frontend → backend)

### AC 1.5.4: Logging Structure ✅
- [ ] Structured JSON logging in backend
- [ ] Log levels: DEBUG, INFO, WARN, ERROR
- [ ] Trace ID included in every log
- [ ] User context included in logs

### AC 1.5.5: Monitoring Dashboard Ready ✅
- [ ] Jaeger UI accessible
- [ ] Can search traces by service
- [ ] Can filter by trace ID
- [ ] Performance metrics visible

---

## Tasks & Subtasks

### Task 1: Set Up Backend Otel
- [ ] Install: opentelemetry-api, opentelemetry-sdk, opentelemetry-exporter-jaeger
- [ ] Install: opentelemetry-instrumentation-fastapi
- [ ] Create otel_config.py with tracer setup
- [ ] Configure Jaeger exporter
- [ ] Add middleware to FastAPI
- [ ] Test with curl request

**Estimated Time:** 1.5 hours

### Task 2: Set Up Frontend Otel
- [ ] Install: @opentelemetry/api, @opentelemetry/sdk-web
- [ ] Install: @opentelemetry/auto-instrumentations-web
- [ ] Install: @opentelemetry/exporter-trace-otlp-http
- [ ] Create otelConfig.ts
- [ ] Configure Jaeger exporter
- [ ] Initialize in main.tsx

**Estimated Time:** 1.5 hours

### Task 3: Instrument Endpoints
- [ ] Add trace decorators to FastAPI routers
- [ ] Add trace context to request/response
- [ ] Trace database queries
- [ ] Trace external API calls (DeepL, Claude)
- [ ] Test trace output

**Estimated Time:** 2 hours

### Task 4: Configure Logging
- [ ] Create structured logger utility
- [ ] Add trace ID to all logs
- [ ] Implement log levels
- [ ] Add context information (user_id, job_id)
- [ ] Test logging output

**Estimated Time:** 1.5 hours

### Task 5: Verify Jaeger Integration
- [ ] Start docker-compose with Jaeger
- [ ] Make requests to backend
- [ ] Verify traces in Jaeger UI
- [ ] Verify end-to-end tracing
- [ ] Check performance waterfall

**Estimated Time:** 1 hour

### Task 6: Write Documentation
- [ ] Document how to add tracing to new endpoints
- [ ] Document how to view traces in Jaeger
- [ ] Document structured logging format
- [ ] Add troubleshooting guide

**Estimated Time:** 1 hour

---

## Dev Notes

**Key Points:**
- OpenTelemetry protocol is vendor-agnostic (can switch to CloudWatch later)
- Jaeger UI available at localhost:16686
- All traces include auto-generated trace IDs
- Logs should include trace context for correlation
- Performance overhead should be minimal

**Architecture:**
```
Frontend → HTTP with trace context
         → Jaeger OTLP Collector
Backend → Instrumented endpoints
        → Jaeger OTLP Exporter
Database queries traced automatically

All → Jaeger UI (localhost:16686)
```

**Resources:**
- docs/architecture.md (Section 9.2: Logging Strategy)
- OpenTelemetry documentation
- Jaeger documentation

---

## Definition of Done

- ✅ All 5 acceptance criteria met
- ✅ All 6 tasks completed
- ✅ Traces visible in Jaeger
- ✅ All endpoints traced
- ✅ Structured logging working
- ✅ Ready for Week 2 development

---

## File List

**New Files:**
- [ ] backend/app/otel_config.py
- [ ] backend/app/logger.py
- [ ] frontend/src/otelConfig.ts
- [ ] backend/app/middleware/tracing.py
- [ ] docs/MONITORING.md (observability guide)

---

## Dev Agent Record

### Debug Log
*To be filled in during development*

### Completion Notes
*To be filled in after story completion*

---

## Status

**Current:** ready-for-dev  
**Last Updated:** 2025-11-15  

---

## Context Reference

- **Story Context File:** docs/sprint-artifacts/1-5-opentelemetry-monitoring.context.xml
- **Architecture Reference:** docs/architecture.md
- **Sprint Plan:** docs/sprint-plan.md

