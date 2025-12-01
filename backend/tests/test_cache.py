"""Redis cache integration tests for TransKeep"""

import json
import os

import pytest
import pytest_asyncio
import redis.asyncio as redis
from redis.asyncio import Redis

from app.cache import Cache, CacheKeys, get_redis_client

# Test Redis URL
TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")


@pytest_asyncio.fixture
async def redis_client() -> Redis:
    """Create Redis client for tests"""
    client = redis.from_url(TEST_REDIS_URL, decode_responses=True)
    yield client
    # Cleanup: flush test database
    await client.flushdb()
    await client.aclose()


class TestRedisConnection:
    """Test Redis connectivity"""

    @pytest.mark.asyncio
    async def test_redis_ping(self, redis_client: Redis):
        """Test Redis connection with ping"""
        result = await redis_client.ping()
        assert result is True

    @pytest.mark.asyncio
    async def test_redis_info(self, redis_client: Redis):
        """Test Redis server info"""
        info = await redis_client.info()
        assert "redis_version" in info


class TestCacheOperations:
    """Test Cache utility class operations"""

    @pytest.mark.asyncio
    async def test_set_and_get(self, redis_client: Redis):
        """Test basic set and get operations"""
        cache = Cache(redis_client)

        await cache.set("test_key", "test_value")
        result = await cache.get("test_key")
        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_set_with_expiration(self, redis_client: Redis):
        """Test set with expiration"""
        cache = Cache(redis_client)

        await cache.set("expire_key", "expire_value", expire_seconds=60)
        ttl = await redis_client.ttl("expire_key")
        assert ttl > 0
        assert ttl <= 60

    @pytest.mark.asyncio
    async def test_delete(self, redis_client: Redis):
        """Test delete operation"""
        cache = Cache(redis_client)

        await cache.set("delete_key", "delete_value")
        assert await cache.exists("delete_key") is True

        await cache.delete("delete_key")
        assert await cache.exists("delete_key") is False

    @pytest.mark.asyncio
    async def test_exists(self, redis_client: Redis):
        """Test exists check"""
        cache = Cache(redis_client)

        assert await cache.exists("nonexistent") is False
        await cache.set("exists_key", "value")
        assert await cache.exists("exists_key") is True

    @pytest.mark.asyncio
    async def test_get_json(self, redis_client: Redis):
        """Test JSON get operation"""
        cache = Cache(redis_client)

        data = {"name": "test", "count": 42, "items": [1, 2, 3]}
        await redis_client.set("json_key", json.dumps(data))

        result = await cache.get_json("json_key")
        assert result == data

    @pytest.mark.asyncio
    async def test_set_json(self, redis_client: Redis):
        """Test JSON set operation"""
        cache = Cache(redis_client)

        data = {"status": "processing", "progress": 50}
        await cache.set_json("json_set_key", data)

        raw = await redis_client.get("json_set_key")
        assert json.loads(raw) == data

    @pytest.mark.asyncio
    async def test_set_json_with_expiration(self, redis_client: Redis):
        """Test JSON set with expiration"""
        cache = Cache(redis_client)

        data = {"cached": True}
        await cache.set_json("json_expire_key", data, expire_seconds=30)

        ttl = await redis_client.ttl("json_expire_key")
        assert ttl > 0
        assert ttl <= 30

    @pytest.mark.asyncio
    async def test_incr(self, redis_client: Redis):
        """Test increment operation"""
        cache = Cache(redis_client)

        result1 = await cache.incr("counter")
        assert result1 == 1

        result2 = await cache.incr("counter")
        assert result2 == 2

        result3 = await cache.incr("counter")
        assert result3 == 3

    @pytest.mark.asyncio
    async def test_expire(self, redis_client: Redis):
        """Test setting expiration on existing key"""
        cache = Cache(redis_client)

        await cache.set("expire_later", "value")
        ttl_before = await redis_client.ttl("expire_later")
        assert ttl_before == -1  # No expiration

        await cache.expire("expire_later", 120)
        ttl_after = await redis_client.ttl("expire_later")
        assert ttl_after > 0
        assert ttl_after <= 120


class TestCacheKeys:
    """Test CacheKeys helper class"""

    def test_session_key(self):
        """Test session key generation"""
        key = CacheKeys.session("user-123")
        assert key == "session:user-123"

    def test_job_status_key(self):
        """Test job status key generation"""
        key = CacheKeys.job_status("job-456")
        assert key == "job:job-456:status"

    def test_job_progress_key(self):
        """Test job progress key generation"""
        key = CacheKeys.job_progress("job-789")
        assert key == "job:job-789:progress"

    def test_blocks_key(self):
        """Test blocks cache key generation"""
        key = CacheKeys.blocks("trans-abc")
        assert key == "blocks:trans-abc"

    def test_rate_limit_key(self):
        """Test rate limit key generation"""
        key = CacheKeys.rate_limit("user-123", "upload")
        assert key == "ratelimit:user-123:upload"

    def test_usage_key(self):
        """Test usage tracking key generation"""
        key = CacheKeys.usage("user-123", "2025-12")
        assert key == "usage:user-123:2025-12"


class TestConcurrentAccess:
    """Test Redis under concurrent access"""

    @pytest.mark.asyncio
    async def test_concurrent_increments(self, redis_client: Redis):
        """Test concurrent increment operations"""
        import asyncio

        cache = Cache(redis_client)
        key = "concurrent_counter"

        # Run 100 concurrent increments
        tasks = [cache.incr(key) for _ in range(100)]
        await asyncio.gather(*tasks)

        # Verify final count
        result = await redis_client.get(key)
        assert int(result) == 100

    @pytest.mark.asyncio
    async def test_concurrent_reads_writes(self, redis_client: Redis):
        """Test concurrent read and write operations"""
        import asyncio

        cache = Cache(redis_client)

        async def write_task(i: int):
            await cache.set(f"concurrent_{i}", f"value_{i}")

        async def read_task(i: int):
            await cache.get(f"concurrent_{i}")

        # Mix of reads and writes
        tasks = []
        for i in range(50):
            tasks.append(write_task(i))
            tasks.append(read_task(i))

        await asyncio.gather(*tasks)

        # Verify some writes succeeded
        for i in range(50):
            result = await cache.get(f"concurrent_{i}")
            assert result == f"value_{i}"

