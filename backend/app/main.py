from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.plugin_manager import plugin_manager
from app.core.redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("Starting up...")
    # 测试Redis连接
    try:
        redis_client.ping()
        print("Redis connected successfully")
    except Exception as e:
        print(f"Redis connection failed: {e}")

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

# 注册插件
plugin_manager.register_plugin("auth", "app.plugins.auth_plugin.plugin")
print("auth_plugin注册成功")
plugin_manager.register_plugin("vehicle", "app.plugins.vehicle_plugin.plugin")
print("vehicle_plugin注册成功")
plugin_manager.register_plugin("test_record", "app.plugins.test_record_plugin.plugin")
print("record_plugin注册成功")
plugin_manager.register_plugin(
    "driver_monitor", "app.plugins.driver_monitor_plugin.plugin"
)
print("driver_monitor_plugin注册成功")
plugin_manager.register_plugin("test_route", "app.plugins.test_route_plugin.plugin")
print("test_route_plugin注册成功")
# plugin_manager.register_plugin("data_analysis", "app.plugins.data_analysis_plugin.plugin")
# print("data_analysis_plugin注册成功")


@app.get("/")
def root():
    return {
        "message": "测试管理平台API",
        "version": "1.0.0",
        "plugins": plugin_manager.list_plugins(),
    }


@app.get("/health")
def health_check():
    health_status = {"status": "healthy", "redis": False}

    try:
        redis_client.ping()
        health_status["redis"] = True
    except:
        pass

    return health_status


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
