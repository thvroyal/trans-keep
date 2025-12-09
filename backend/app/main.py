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
from app.routers.auth import router as auth_router
from app.routers.upload import router as upload_router
from app.s3 import create_bucket_if_not_exists
from app.otel_config import init_telemetry, instrument_app
from app.logger import info, error


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events"""
    # Startup
    info("TransKeep backend starting up")
    
    # Initialize OpenTelemetry
    try:
        init_telemetry("transkeep-backend")
        info("OpenTelemetry initialized successfully")
    except Exception as e:
        error("Failed to initialize OpenTelemetry", exc=e)
    
    # Create S3 bucket if it doesn't exist (for local MinIO)
    settings = get_settings()
    if settings.s3_endpoint_url:
        try:
            await create_bucket_if_not_exists()
            info("S3 bucket ready")
        except Exception as e:
            error("Could not create S3 bucket", exc=e)

    yield

    # Shutdown
    info("TransKeep backend shutting down")
    await close_db()
    await close_redis()


# Initialize FastAPI app
app = FastAPI(
    title="TransKeep API",
    description="Document translation with format preservation",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for local development (add before instrumentation)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument FastAPI and libraries with OpenTelemetry
try:
    instrument_app(app)
except Exception as e:
    error("Failed to instrument FastAPI app", exc=e)

# Include routers
app.include_router(auth_router)
app.include_router(upload_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"status": "ok", "message": "TransKeep API is running"}


@app.get("/health")
async def health(settings = Depends(get_settings)):
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
    settings = Depends(get_settings),
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
