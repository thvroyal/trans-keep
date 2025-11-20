# TransKeep - Document Translation with Format Preservation

A modern web application for translating documents while preserving their original format. Upload PDFs, view side-by-side translations, customize translation tone, and download results.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- OR: Node.js 20+, Python 3.11+, and uv package manager

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up --build

# Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Jaeger UI: http://localhost:16686
- PostgreSQL: localhost:5432
- Redis: localhost:6379
```

### Local Development Setup

#### Frontend
```bash
cd frontend
npm install
npm run dev
# Access at http://localhost:5173
```

#### Backend
```bash
cd backend
source .venv/bin/activate  # or uv pip sync
uv pip install -e .
uvicorn app.main:app --reload
# Access at http://localhost:8000
```

## 📁 Project Structure

```
trans-keep/
├── frontend/              # React 18 + TypeScript + Vite
│   ├── src/
│   ├── vite.config.ts
│   ├── package.json
│   └── Dockerfile.dev
├── backend/               # FastAPI + Python 3.11
│   ├── app/
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml     # Local dev orchestration
├── .github/workflows/     # CI/CD pipelines
└── docs/                  # Documentation
```

## 🛠 Tech Stack

### Frontend
- **Framework:** React 18 + TypeScript
- **Bundler:** Vite
- **UI Components:** shadcn/ui + Tailwind CSS
- **State:** Zustand
- **HTTP Client:** TanStack Query
- **Package Manager:** npm/pnpm

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Package Manager:** uv
- **Database:** PostgreSQL 15
- **Cache:** Redis 7
- **Task Queue:** Celery
- **Observability:** OpenTelemetry + Jaeger
- **APIs:** DeepL (translation), Claude (tone customization)

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Docker Compose (local), AWS ECS (production)
- **File Storage:** AWS S3
- **CI/CD:** GitHub Actions

## 📚 Documentation

- **Architecture:** [docs/architecture.md](docs/architecture.md)
- **Sprint Plan:** [docs/sprint-plan.md](docs/sprint-plan.md)
- **PRD:** [docs/PRD.md](docs/PRD.md)
- **UX Design:** [docs/ux-design-specification.md](docs/ux-design-specification.md)
- **Python Setup:** [docs/uv-setup-guide.md](docs/uv-setup-guide.md)

## 🔧 Development

### Running Tests

**Frontend:**
```bash
cd frontend
npm run test
```

**Backend:**
```bash
cd backend
pytest tests/ -v
```

### Code Quality

**Frontend:**
```bash
cd frontend
npm run lint
npm run format
```

**Backend:**
```bash
cd backend
ruff check app/
black app/
mypy app/
```

## 🚢 Deployment

See [docs/architecture.md](docs/architecture.md#deployment) for production deployment guidelines.

### Local Docker Build
```bash
docker-compose build
docker-compose up
```

### Production Deployment
- Frontend: CloudFront + S3
- Backend: AWS ECS
- Database: RDS PostgreSQL
- Cache: ElastiCache Redis

## 📊 Environment Variables

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_client_id_here
```

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@localhost:5432/transkeep
REDIS_URL=redis://localhost:6379
DEEPL_API_KEY=your_api_key
CLAUDE_API_KEY=your_api_key
```

See `.env.example` files for complete reference.

## 🔐 Security

- OAuth 2.0 via Google for authentication
- JWT tokens for API requests
- Multi-tenant data isolation
- HTTPS enforced in production
- No sensitive data in logs

## 🐛 Troubleshooting

### Docker Services Won't Start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild
docker-compose build --no-cache
```

### Port Already in Use
Change ports in `docker-compose.yml` or kill existing processes:
```bash
lsof -i :3000  # Find process on port 3000
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps

# Reset database
docker-compose down -v
docker-compose up postgres
```

## 📞 Support

For issues or questions:
1. Check existing documentation in `/docs`
2. Review GitHub Issues
3. See troubleshooting section above

## 📝 License

[Specify your license here]

## 👥 Contributing

[Contributing guidelines here]

---

**Status:** MVP Development (Week 1-4)  
**Last Updated:** 2025-11-14

