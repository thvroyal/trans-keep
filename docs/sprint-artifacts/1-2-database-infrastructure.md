# Story 1.2: Database & Infrastructure Setup

**Story Key:** 1-2-database-infrastructure  
**Epic:** 1 - Setup & Scaffolding  
**Week:** Week 1 (Dec 2-6)  
**Duration:** 1 day  
**Owner:** Backend Developer  
**Status:** ready-for-dev (context generated)  

---

## Overview

Set up persistent data storage with PostgreSQL, caching layer with Redis, file storage with S3, and database migration framework with Alembic. All services configured and tested locally via Docker Compose.

---

## Acceptance Criteria

### AC 1.2.1: PostgreSQL Schema Created ✅
- [ ] Users table with Google OAuth integration
- [ ] Translations table with job status tracking
- [ ] DocumentBlocks table for extracted text blocks
- [ ] All tables with proper indexes and constraints
- [ ] Foreign keys properly configured

### AC 1.2.2: Redis Cache Layer Ready ✅
- [ ] Redis service running in Docker Compose
- [ ] Redis connection pooling configured
- [ ] Session caching configured
- [ ] Celery broker configured to use Redis

### AC 1.2.3: S3 Bucket Setup ✅
- [ ] Local S3 (MinIO) configured for dev
- [ ] AWS S3 bucket created for production
- [ ] IAM policy configured (least privilege)
- [ ] boto3 client properly configured

### AC 1.2.4: Alembic Migrations ✅
- [ ] Alembic initialized in backend
- [ ] Initial migration created for schema
- [ ] Migration runs successfully: `alembic upgrade head`
- [ ] Rollback works: `alembic downgrade -1`

### AC 1.2.5: Environment Variables ✅
- [ ] DATABASE_URL configured
- [ ] REDIS_URL configured
- [ ] AWS_REGION, AWS_BUCKET_NAME configured
- [ ] All secrets in .env (not committed)

---

## Tasks & Subtasks

### Task 1: Create PostgreSQL Schema
- [ ] Connect to PostgreSQL from backend
- [ ] Create Users table (id, google_id, email, name, created_at)
- [ ] Create Translations table (id, user_id, status, original_path, translated_path)
- [ ] Create DocumentBlocks table (id, translation_id, page_num, block_num, original_text, translated_text, coordinates)
- [ ] Create Glossary table (id, user_id, term, translation, target_lang)
- [ ] Add indexes on frequently queried columns
- [ ] Add foreign key constraints

**Estimated Time:** 2 hours

### Task 2: Configure Redis Connection
- [ ] Install redis-py and aioredis
- [ ] Create Redis connection pool in config
- [ ] Add health check endpoint
- [ ] Test connection with simple get/set

**Estimated Time:** 1 hour

### Task 3: Set Up S3 Integration
- [ ] Create MinIO (local S3) bucket for development
- [ ] Create AWS S3 bucket for production
- [ ] Configure IAM policy (GetObject, PutObject, DeleteObject)
- [ ] Update boto3 client with proper configuration
- [ ] Create utility functions: upload_file, download_file, delete_file

**Estimated Time:** 1.5 hours

### Task 4: Initialize Alembic
- [ ] Run `alembic init migrations`
- [ ] Update alembic.ini with DATABASE_URL
- [ ] Create initial migration from SQLAlchemy models
- [ ] Test migration: upgrade and downgrade
- [ ] Document migration workflow

**Estimated Time:** 1.5 hours

### Task 5: Update Environment Configuration
- [ ] Add DATABASE_URL to backend/.env
- [ ] Add REDIS_URL to backend/.env
- [ ] Add AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
- [ ] Add AWS_REGION, AWS_BUCKET_NAME
- [ ] Add S3_ENDPOINT_URL for local development
- [ ] Update .env.example with all variables

**Estimated Time:** 30 minutes

### Task 6: Write Integration Tests
- [ ] Test database connection
- [ ] Test schema creation
- [ ] Test Redis connection
- [ ] Test S3 bucket access
- [ ] Test migration rollback

**Estimated Time:** 1.5 hours

---

## Dev Notes

**Key Points:**
- Use SQLAlchemy ORM for all database operations
- Redis for session caching (production) and Celery broker
- S3 for file storage with cleanup after 24 hours
- Alembic for version control of schema changes
- All database operations should be async-safe

**Resources:**
- docs/architecture.md (Section 5: Data Models)
- SQLAlchemy documentation
- Alembic documentation
- boto3 documentation

---

## Definition of Done

- ✅ All 5 acceptance criteria met
- ✅ All 6 tasks completed and checked
- ✅ Integration tests passing
- ✅ `docker-compose up` starts postgres, redis, and backend
- ✅ Database connection verified
- ✅ Migrations run successfully
- ✅ Ready for Story 1.3

---

## File List

**New Files:**
- [ ] backend/app/models/ (SQLAlchemy models)
- [ ] backend/migrations/ (Alembic migrations)
- [ ] backend/app/database.py (database connection)
- [ ] backend/app/cache.py (Redis connection)
- [ ] backend/app/s3.py (S3 utilities)
- [ ] backend/tests/test_database.py (integration tests)

---

## Dev Agent Record

### Debug Log
*To be filled in during development*

### Completion Notes
*To be filled in after story completion*

---

## Change Log

*Document all changes as they're made*

---

## Status

**Current:** ready-for-dev  
**Last Updated:** 2025-11-15  
**Next:** Start implementation

---

## Context Reference

- **Story Context File:** docs/sprint-artifacts/1-2-database-infrastructure.context.xml
- **Architecture Reference:** docs/architecture.md
- **Sprint Plan:** docs/sprint-plan.md

