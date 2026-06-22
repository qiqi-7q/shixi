from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.core.config import settings
from app.core.plugin_manager import plugin_manager
from app.core.redis_client import redisserve
from app.core.scheduler import stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("Starting up...")
    # 测试 Redis 连接
    redis_result = await redisserve.conn_ping()
    print(redis_result)

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
    # 新增的三个插件注册
    await plugin_manager.register_plugin(
        "employee", "app.plugins.employee_plugin.plugin"
    )
    await plugin_manager.register_plugin(
        "test_miles", "app.plugins.test_miles_plugin.plugin"
    )
    await plugin_manager.register_plugin(
        "test_task", "app.plugins.test_task_plugin.plugin"
    )
    await plugin_manager.register_plugin(
        "data_analysis", "app.plugins.data_analysis_plugin.plugin"
    )

    yield
    # 关闭时执行
    stop_scheduler()
    print("Shutting down...")
    await redisserve.close_conn()


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

# # 项目根目录（app文件夹）
# BASE_DIR = Path(__file__).parent
# # 静态文件目录
# STATIC_DIR = BASE_DIR / "static"
# # 上传文件目录
# UPLOAD_DIR = BASE_DIR / "uploads"

# 文件夹不存在则自动创建
settings.STATIC_DIR.mkdir(exist_ok=True, parents=True)
settings.UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

# ========== 挂载静态文件 ==========
# 访问地址：http://127.0.0.1:8000/static/xxx.png
app.mount(path="/static", app=StaticFiles(directory=settings.STATIC_DIR), name="static")


@app.get("/")
async def root():
    return {
        "message": "测试管理平台API",
        "version": "1.0.0",
        "plugins": plugin_manager.list_plugins(),
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "redis": await redisserve.conn_ping()}


if __name__ == "__main__":
    # uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    uvicorn.run("app.main:app", host="10.192.183.119", port=8000, reload=True)
