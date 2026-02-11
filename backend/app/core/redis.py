import redis.asyncio as redis
from .config import settings

class RedisClient:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self.redis

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def ping(self):
        if self.redis:
            return await self.redis.ping()
        return False

    async def set(self, key: str, value: str, ex: int = None):
        if self.redis:
            return await self.redis.set(key, value, ex=ex)
        return False

    async def get(self, key: str):
        if self.redis:
            return await self.redis.get(key)
        return None

    async def delete(self, key: str):
        if self.redis:
            return await self.redis.delete(key)
        return False

    async def exists(self, key: str):
        if self.redis:
            return await self.redis.exists(key)
        return False

    async def expire(self, key: str, seconds: int):
        if self.redis:
            return await self.redis.expire(key, seconds)
        return False

    async def incr(self, key: str):
        if self.redis:
            return await self.redis.incr(key)
        return 0

    async def lpush(self, key: str, *values):
        if self.redis:
            return await self.redis.lpush(key, *values)
        return 0

    async def rpop(self, key: str):
        if self.redis:
            return await self.redis.rpop(key)
        return None

    async def llen(self, key: str):
        if self.redis:
            return await self.redis.llen(key)
        return 0

redis_client = RedisClient()

async def init_redis():
    await redis_client.connect()
