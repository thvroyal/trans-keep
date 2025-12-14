# 5. Infrastructure & Deployment

## 5.1 Local Development (Docker Compose)

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/transkeep
      REDIS_URL: redis://redis:6379
      DEEPL_API_KEY: ${DEEPL_API_KEY}
      CLAUDE_API_KEY: ${CLAUDE_API_KEY}
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: transkeep
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: ./backend
    command: celery -A app.workers.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/transkeep
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000

volumes:
  postgres_data:
```

**Local Development Workflow:**
```bash
# Start all services
docker-compose up

# Endpoints available:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs (Swagger)
```

## 5.2 Production Deployment (AWS)

**Infrastructure:**

| Component | AWS Service | Rationale |
|-----------|-------------|-----------|
| **Frontend** | CloudFront + S3 | CDN for React SPA, static assets |
| **Backend** | ECS (Fargate) | Containerized FastAPI, auto-scaling |
| **Database** | RDS PostgreSQL | Managed, replicated, backups |
| **Cache** | ElastiCache Redis | Managed Redis for Celery queue |
| **File Storage** | S3 | Scalable, cheap, CDN-integrated |
| **Jobs** | ECS Tasks | Celery workers as containerized tasks |
| **Secrets** | Secrets Manager | Store API keys, DB passwords |
| **Monitoring** | CloudWatch | Logs, metrics, alarms |
| **Load Balancing** | ALB | Distribute traffic to ECS tasks |

**Deployment Pipeline:**
```
1. Code pushed to GitHub
2. GitHub Actions triggers CI/CD
3. Build Docker image (backend & frontend)
4. Push to ECR (Elastic Container Registry)
5. Deploy to ECS:
   - Update backend service
   - Update Celery workers
   - Deploy static assets to S3
6. CloudFront invalidates cache
7. Health checks verify deployment
8. Monitoring alerts on failures
```

## 5.3 Scalability Strategy

**Horizontal Scaling (Auto-scaling):**
- Backend: ECS auto-scales based on CPU/memory
- Celery workers: Scale up during peak upload times
- Database: RDS read replicas for high query load (Phase 2)

**Rate Limiting:**
- Per-user: 10 requests/minute (prevent abuse)
- Per-tenant: 100 documents/month (freemium limit)
- S3: Automatic (AWS handles)

**Caching Strategy:**
- Redis: Cache user sessions, job status
- CloudFront: Cache download links (24 hours)
- Browser: Cache static assets with long TTL

---
