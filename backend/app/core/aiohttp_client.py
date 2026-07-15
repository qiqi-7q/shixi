import aiohttp

# 全局会话实例，延迟初始化
_session: aiohttp.ClientSession | None = None


# 全局连接器统一配置（超时、代理、ssl、连接池大小统一管控）
def create_connector() -> aiohttp.TCPConnector:
    return aiohttp.TCPConnector(limit=10, verify_ssl=False)  # 全局最大并发连接数


def create_timeout() -> aiohttp.ClientTimeout:
    return aiohttp.ClientTimeout(total=20)


async def get_session() -> aiohttp.ClientSession:
    """获取全局唯一session，不存在则初始化"""
    global _session
    if _session is None or _session.closed:
        connector = create_connector()
        timeout = create_timeout()
        _session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    return _session


async def close_session():
    """应用退出时关闭连接池，释放资源"""
    global _session
    if _session and not _session.closed:
        await _session.close()
