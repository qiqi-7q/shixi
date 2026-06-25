import uuid

from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings


class RedisService:

    def __init__(self):
        self.redis_pool = ConnectionPool.from_url(
            f"{settings.REDIS_URL}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            password=settings.REDIS_PASSWORD,
        )
        self.redis_client = Redis(
            connection_pool=self.redis_pool, decode_responses=True, max_connections=30
        )

    async def set_data(self, key: str, value: str, expire_seconds: int = 1800):
        """存储数据到Redis"""
        await self.redis_client.setex(key, expire_seconds, value)

    async def get_data(self, key: str) -> str:
        """从Redis获取数据"""
        return await self.redis_client.get(key)

    async def delete_data(self, key: str):
        """从Redis删除数据"""
        await self.redis_client.delete(key)

    # 检查数据是否存在
    async def exists_data(self, key: str) -> bool:
        """检查数据是否存在"""
        return await self.redis_client.exists(key) == 1

    # 分布式锁
    async def acquire_lock(self, lock_key: str, expire_seconds: int = 5):
        """获取锁"""
        client_id = str(uuid.uuid4())
        return (
            client_id
            if await self.redis_client.set(
                lock_key, client_id, nx=True, ex=expire_seconds
            )
            else None
        )

    # lua脚本，用于释放锁或检查锁是否被释放
    async def lua_script(self, lock_key: str, client_id: str):
        """执行lua脚本"""
        script = """
            if redis.call('GET', KEYS[1]) == ARGV[1] then
                return redis.call('DEL', KEYS[1])
            end
            return 0
            """
        return await self.redis_client.eval(script, 1, lock_key, client_id)

    async def renew_lock(self, lock_key: str, client_id: str, expire_seconds: int):
        """刷新锁过期时间"""
        lua_renew = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("EXPIRE", KEYS[1], ARGV[2])
        end
        return 0
        """
        res = await self.redis_client.eval(
            lua_renew, 1, lock_key, client_id, expire_seconds
        )
        return res == 1

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

    # 断开Redis连接
    async def close_conn(self):
        """断开Redis连接"""
        await self.redis_client.close()


redisserve = RedisService()
