from redis.asyncio import Redis

from app.core.config import settings


class RedisService:

    def __init__(self):
        # 使用 RESP2 协议，解决 Redis 7+ 的 HELLO 认证问题
        connection_kwargs = {
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "db": settings.REDIS_DB,
            "decode_responses": True,
            "max_connections": 30,
            "protocol": 2,  # 强制使用 RESP2 协议
        }

        if settings.REDIS_PASSWORD:
            connection_kwargs["password"] = settings.REDIS_PASSWORD

        self.redis_client = Redis(**connection_kwargs)

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
