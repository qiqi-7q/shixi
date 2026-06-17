from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings


class RedisService:

    def __init__(self):
        self.redis_pool = ConnectionPool.from_url(
            f"{settings.REDIS_URL}{settings.REDIS_DB}"
        )
        self.redis_client = Redis(
            connection_pool=self.redis_pool, decode_responses=True, max_connections=30
        )

    async def set_token(self, user_id: int, token: str, expire_seconds: int = 1800):
        """存储用户token到Redis"""
        key = f"user_token:{user_id}"
        await self.redis_client.setex(key, expire_seconds, token)

    async def get_token(self, user_id: int) -> str:
        """获取用户token"""
        key = f"user_token:{user_id}"
        return await self.redis_client.get(key)

    async def delete_token(self, user_id: int):
        """删除用户token"""
        key = f"user_token:{user_id}"
        await self.redis_client.delete(key)

    async def blacklist_token(self, token: str, expire_seconds: int = 1800):
        """将token加入黑名单"""
        key = f"blacklist:{token}"
        await self.redis_client.setex(key, expire_seconds, "1")

    async def is_token_blacklisted(self, token: str) -> bool:
        """检查token是否在黑名单中"""
        key = f"blacklist:{token}"
        return await self.redis_client.exists(key) == 1

    async def conn_ping(self) -> str:
        """检查Redis连接是否正常"""
        try:
            await self.redis_client.ping()
            return "Redis连接成功"
        except Exception as e:
            return f"Redis连接异常: {str(e)}"


redisserve = RedisService()
