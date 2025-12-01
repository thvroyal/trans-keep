"""FastAPI application entry point for TransKeep backend"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import close_redis, get_redis
from app.config import get_settings
from app.database import close_db, get_db
from app.s3 import create_bucket_if_not_exists

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events"""
    # Startup
    # Create S3 bucket if it doesn't exist (for local MinIO)
    if settings.s3_endpoint_url:
        try:
            await create_bucket_if_not_exists()
        except Exception as e:
            print(f"Warning: Could not create S3 bucket: {e}")

    yield

    # Shutdown
    await close_db()
    await close_redis()


# Initialize FastAPI app
app = FastAPI(
    title="TransKeep API",
    description="Document translation with format preservation",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"status": "ok", "message": "TransKeep API is running"}


@app.get("/health")
async def health():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "TransKeep Backend",
        "version": settings.app_version,
    }


@app.get("/health/detailed")
async def health_detailed(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Detailed health check including database and Redis connectivity.
    
    Returns status of all infrastructure components.
    """
    health_status = {
        "status": "healthy",
        "service": "TransKeep Backend",
        "version": settings.app_version,
        "components": {},
    }

    # Check PostgreSQL
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        health_status["components"]["database"] = {
            "status": "healthy",
            "type": "postgresql",
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "type": "postgresql",
            "error": str(e),
        }
        health_status["status"] = "degraded"

    # Check Redis
    try:
        await redis.ping()
        health_status["components"]["redis"] = {
            "status": "healthy",
            "type": "redis",
        }
    except Exception as e:
        health_status["components"]["redis"] = {
            "status": "unhealthy",
            "type": "redis",
            "error": str(e),
        }
        health_status["status"] = "degraded"

    return health_status


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
