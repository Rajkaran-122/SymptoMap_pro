"""
Redis client setup with Mock fallback
"""

import time
import redis.asyncio as redis
from app.core.config import settings


class MockRedis:
    """In-memory Redis mock for local development with TTL support."""

    def __init__(self):
        # key -> (value, expires_at_epoch|None)
        self.store = {}
        print("WARNING: Using In-Memory Mock Redis (data resets on restart)")

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    async def get(self, key):
        item = self.store.get(key)
        if item is None:
            return None

        # Backward compatibility for any legacy plain values.
        if not isinstance(item, tuple) or len(item) != 2:
            return item

        value, expires_at = item
        if expires_at is not None and time.time() >= expires_at:
            self.store.pop(key, None)
            return None
        return value

    async def set(self, key, value, ex=None):
        expires_at = None
        if ex is not None:
            try:
                expires_at = time.time() + int(ex)
            except Exception:
                expires_at = None
        self.store[key] = (value, expires_at)

    async def delete(self, key):
        self.store.pop(key, None)

    async def exists(self, key):
        value = await self.get(key)
        return 1 if value is not None else 0


class RedisClient:
    """Async Redis client wrapper"""

    def __init__(self):
        self.redis = None
        self.use_mock = False

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,
            )
            await self.redis.ping()
            print("Connected to Redis")
        except Exception as e:
            print(f"Redis connection failed: {e}")
            print("Switching to Mock Redis...")
            self.use_mock = True
            self.redis = MockRedis()

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis and not self.use_mock:
            await self.redis.close()

    async def get(self, key: str) -> str:
        """Get value from Redis"""
        if not self.redis:
            await self.connect()
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ex: int = None):
        """Set value in Redis with optional expiry"""
        if not self.redis:
            await self.connect()
        await self.redis.set(key, value, ex=ex)

    async def delete(self, key: str):
        """Delete key from Redis"""
        if not self.redis:
            await self.connect()
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis:
            await self.connect()
        return await self.redis.exists(key)

    async def publish(self, channel: str, message: dict):
        """Publish a JSON message to a Redis channel"""
        if not self.redis:
            await self.connect()
        
        if self.use_mock:
            # Simple mock implementation: fire and forget to standard out
            import json
            print(f"[MockRedis PubSub] Published to {channel}: {json.dumps(message)}")
            return
            
        import json
        await self.redis.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str):
        """
        Subscribe to a Redis channel and yield incoming messages.
        Use as an async generator:
        async for message in redis_client.subscribe("channel"):
            ...
        """
        if not self.redis:
            await self.connect()
            
        if self.use_mock:
            # Mock implementation: just yield an empty loop that waits
            import asyncio
            print(f"[MockRedis PubSub] Subscribed to {channel} (No-op loop)")
            try:
                while True:
                    await asyncio.sleep(3600)
            except asyncio.CancelledError:
                pass
            return

        import json
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        print(f"Subscribed to Redis channel: {channel}")
        
        try:
            async for raw_message in pubsub.listen():
                if raw_message["type"] == "message":
                    try:
                        data = json.loads(raw_message["data"])
                        yield data
                    except json.JSONDecodeError:
                        yield raw_message["data"]
        finally:
            await pubsub.unsubscribe(channel)


redis_client = RedisClient()
