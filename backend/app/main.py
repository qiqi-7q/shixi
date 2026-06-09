from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.plugin_manager import plugin_manager
from app.core.redis_client import redisserve


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("Starting up...")
    # 测试Redis连接
    try:
        await redisserve.ping()
        print("Redis connected successfully")
    except Exception as e:
        print(f"Redis connection failed: {e}")

    # 注册插件
    await plugin_manager.register_plugin("auth", "app.plugins.auth_plugin.plugin")
    await plugin_manager.register_plugin("vehicle", "app.plugins.vehicle_plugin.plugin")
    await plugin_manager.register_plugin(
        "test_record", "app.plugins.test_record_plugin.plugin"
    )
    await plugin_manager.register_plugin(
        "driver_monitor", "app.plugins.driver_monitor_plugin.plugin"
    )
    await plugin_manager.register_plugin(
        "test_route", "app.plugins.test_route_plugin.plugin"
    )

    yield
    # 关闭时执行
    print("Shutting down...")


app = FastAPI(
    title="测试管理平台",
    description="基于FastAPI的测试管理平台",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化插件管理器
plugin_manager.init_app(app)


@app.get("/")
async def root():
    return {
        "message": "测试管理平台API",
        "version": "1.0.0",
        "plugins": plugin_manager.list_plugins(),
    }


@app.get("/health")
async def health_check():
    health_status = {"status": "healthy", "redis": False}

    try:
        await redisserve.ping()
        health_status["redis"] = True
    except:
        pass

    return health_status


if __name__ == "__main__":
    # uvicorn.run("app.main:app", host="10.192.183.23", port=8000, reload=True)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
