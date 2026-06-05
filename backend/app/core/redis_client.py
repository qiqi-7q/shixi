import redis
from app.core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)


class RedisService:
    @staticmethod
    def set_token(user_id: int, token: str, expire_seconds: int = 1800):
        """存储用户token到Redis"""
        key = f"user_token:{user_id}"
        redis_client.setex(key, expire_seconds, token)

    @staticmethod
    def get_token(user_id: int) -> str:
        """获取用户token"""
        key = f"user_token:{user_id}"
        return redis_client.get(key)

    @staticmethod
    def delete_token(user_id: int):
        """删除用户token"""
        key = f"user_token:{user_id}"
        redis_client.delete(key)

    @staticmethod
    def blacklist_token(token: str, expire_seconds: int = 1800):
        """将token加入黑名单"""
        key = f"blacklist:{token}"
        redis_client.setex(key, expire_seconds, "1")

    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """检查token是否在黑名单中"""
        key = f"blacklist:{token}"
        return redis_client.exists(key) == 1