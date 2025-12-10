"""Redis cache connection and utilities"""

from collections.abc import AsyncGenerator
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from app.config import get_settings

settings = get_settings()

# Create Redis connection pool
redis_pool = redis.ConnectionPool.from_url(
    settings.redis_url,
    max_connections=10,
    decode_responses=True,
)


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Dependency injection for Redis client.
    
    Usage:
        @app.get("/cached")
        async def get_cached(redis: Redis = Depends(get_redis)):
            value = await redis.get("key")
            ...
    """
    client = Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.aclose()


def get_redis_client() -> Redis:
    """Get a Redis client (non-generator version for internal use)"""
    return Redis(connection_pool=redis_pool)


async def close_redis() -> None:
    """Close Redis connection pool"""
    await redis_pool.disconnect()


# Cache utility functions
class Cache:
    """Redis cache utility class"""

    def __init__(self, client: Redis):
        self.client = client

    async def get(self, key: str) -> str | None:
        """Get value from cache"""
        return await self.client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        expire_seconds: int | None = None,
    ) -> bool:
        """Set value in cache with optional expiration"""
        if expire_seconds:
            return await self.client.setex(key, expire_seconds, value)
        return await self.client.set(key, value)

    async def delete(self, key: str) -> int:
        """Delete key from cache"""
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        return await self.client.exists(key) > 0

    async def get_json(self, key: str) -> dict | list | None:
        """Get JSON value from cache"""
        import json

        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(
        self,
        key: str,
        value: dict | list,
        expire_seconds: int | None = None,
    ) -> bool:
        """Set JSON value in cache"""
        import json

        json_str = json.dumps(value)
        return await self.set(key, json_str, expire_seconds)

    async def incr(self, key: str) -> int:
        """Increment counter"""
        return await self.client.incr(key)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on existing key"""
        return await self.client.expire(key, seconds)


# Cache key prefixes
class CacheKeys:
    """Cache key prefix constants"""

    # Session keys
    SESSION = "session:{user_id}"

    # Job status keys
    JOB_STATUS = "job:{job_id}:status"
    JOB_PROGRESS = "job:{job_id}:progress"

    # Extracted blocks (cached for 24 hours)
    BLOCKS = "blocks:{translation_id}"

    # Rate limiting
    RATE_LIMIT = "ratelimit:{user_id}:{action}"

    # User usage tracking
    USAGE = "usage:{user_id}:{month}"

    @classmethod
    def session(cls, user_id: str) -> str:
        return cls.SESSION.format(user_id=user_id)

    @classmethod
    def job_status(cls, job_id: str) -> str:
        return cls.JOB_STATUS.format(job_id=job_id)

    @classmethod
    def job_progress(cls, job_id: str) -> str:
        return cls.JOB_PROGRESS.format(job_id=job_id)

    @classmethod
    def blocks(cls, translation_id: str) -> str:
        return cls.BLOCKS.format(translation_id=translation_id)

    @classmethod
    def rate_limit(cls, user_id: str, action: str) -> str:
        return cls.RATE_LIMIT.format(user_id=user_id, action=action)

    @classmethod
    def usage(cls, user_id: str, month: str) -> str:
        return cls.USAGE.format(user_id=user_id, month=month)

