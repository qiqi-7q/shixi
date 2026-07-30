from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from jose import JWTError, jwt
from app.core.aiohttp_client import close_session
from app.core.config import settings
from app.core.database import Base
from app.core.plugin_manager import plugin_manager


from app.core.redis_client import redisserve

from app.core.scheduler import scheduler, stop_scheduler
from app.utils.json_operator import init_model_meta_cache, labels_router
from app.utils.upload_files import upload_router

from app.plugins.driver_monitor_plugin.services import WebSocketService as _ws
from app.plugins.driver_monitor_plugin.services import WebSocketService,DriverMonitorService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("Starting up...")
    # 测试 Redis 连接
    redis_result = await redisserve.conn_ping()
    print(redis_result)

    # 2. 启动定时调度器（配置中jobs已自动注册，只需start）
    if not scheduler.running:
        scheduler.start()
        print("APScheduler 调度器启动成功，所有定时任务加载完成")

    # 注册插件
    await plugin_manager.register_plugin("auth", "app.plugins.auth_plugin.plugin")
    await plugin_manager.register_plugin("vehicle", "app.plugins.vehicle_plugin.plugin")
    await plugin_manager.register_plugin(
        "test_record", "app.plugins.test_record_plugin.plugin"
    )
    await plugin_manager.register_plugin(
        "test_route", "app.plugins.test_route_plugin.plugin"
    )
    await plugin_manager.register_plugin(
        "employee", "app.plugins.employee_plugin.plugin"
    )
    await plugin_manager.register_plugin(
        "test_miles", "app.plugins.test_miles_plugin.plugin"
    )
    await plugin_manager.register_plugin(
        "data_analysis", "app.plugins.data_analysis_plugin.plugin"
    )
    await plugin_manager.register_plugin(
        "vehicle_monitor", "app.plugins.vehicle_monitor_plugin.plugin"
    )
    await plugin_manager.register_plugin(
        "driver_monitor", "app.plugins.driver_monitor_plugin.plugin"
    )
    # await plugin_manager.register_plugin(
    #     "test_task", "app.plugins.test_task_plugin.plugin"
    # )
    # await plugin_manager.register_plugin(
    #     "project_plan", "app.plugins.project_plan_plugin.plugin"
    # )

    # 3. 初始化数据库模型元数据缓存
    init_model_meta_cache(Base)

    # 4. 自动启动 iotsmart WebSocket 长连接
    await WebSocketService.start()
    print("iotsmart WebSocket 服务已自动启动")

    yield
    # 关闭时执行
    print("Shutting down...")
    _ws.stop()
    stop_scheduler()
    await redisserve.close_conn()
    await close_session()


app = FastAPI(
    title="测试管理平台",
    description="基于FastAPI的测试管理平台",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.SWAGGER_ENABLED else None,
    redoc_url="/redoc" if settings.SWAGGER_ENABLED else None,
)


# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# 初始化插件管理器
plugin_manager.init_app(app)


# 文件夹不存在则自动创建
settings.STATIC_DIR.mkdir(exist_ok=True, parents=True)
settings.UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

# ========== 挂载静态文件 ==========
app.mount(path="/static", app=StaticFiles(directory=settings.STATIC_DIR), name="static")

# ========== 注册通用文件上传路由 ==========
app.include_router(upload_router, prefix="/api", tags=["通用文件上传"])
# ========== 注册模块标签操作路由 ==========
app.include_router(labels_router, prefix="/api", tags=["模块标签操作"])


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


from fastapi import WebSocket, WebSocketDisconnect
from app.core.ws_client import ws_manager


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket 连接端点
    前端连接地址：ws://127.0.0.1:8000/ws/{client_id}
    client_id 为客户端唯一标识，用于消息定向推送。
    """
    await ws_manager.connect(client_id, websocket)
    try:
        while True:
            # 接收消息（保持连接活跃，同时可处理客户端发来的消息）
            data = await websocket.receive_text()
            # 可在此处处理客户端上行消息
            # print(f"Received message from {client_id}: {data}")
            # # 示例：回显消息给客户端
            # await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
    except Exception:
        ws_manager.disconnect(client_id)


# ==================== SSE 接口 ====================
from app.core.sse_client import sse_mgr
from starlette.requests import Request
from starlette.responses import StreamingResponse
import asyncio


@app.get("/sse/sub")
async def sse_subscribe(request: Request, username: str):
    """SSE 订阅端点（统一入口，所有业务推送共用此连接，用 event 区分）

    前端连接示例：
        const es = new EventSource('/sse/sub?username=user_001');
        es.addEventListener('alert', e => console.log(JSON.parse(e.data)));
        es.addEventListener('vehicle_online_list', e => console.log(JSON.parse(e.data)));
        es.addEventListener('vehicle_status', e => console.log(JSON.parse(e.data)));
        es.addEventListener('location', e => console.log(JSON.parse(e.data)));
    """
    queue = await sse_mgr.subscribe(username)

    async def event_generator():
        try:
            from app.plugins.driver_monitor_plugin import services as _dm_services
            WebSocketService = _dm_services.WebSocketService

            # 1. 如果WS在运行：
            if WebSocketService.is_running():
                if _dm_services._online_list_initialized:
                    # 真实数据已就绪：推真实快照
                    snapshot = DriverMonitorService.get_online_vehicle_snapshot()
                    if snapshot:
                        msg = sse_mgr._build_message(
                            {"data": snapshot},
                            event="vehicle_online_list",
                        )
                        await queue.put(msg)
            # 2. WS没启动：自动启动WS（前端连SSE即自动触发）
            else:
                asyncio.create_task(WebSocketService.start())
        except Exception:
            pass

        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=25)
                    yield payload
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
        finally:
            await sse_mgr.unsubscribe(username, queue)

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # 关闭 Nginx 缓冲
    }
    return StreamingResponse(event_generator(), headers=headers)


@app.get("/sse/sub_device")
async def sse_subscribe_device(request: Request, username: str, devNo: str):
    """按设备号订阅 SSE（只接收指定设备的消息）

    前端连接示例：
        const es = new EventSource('/sse/sub_device?username=user_001&devNo=527086498786');
        es.addEventListener('location', e => console.log(JSON.parse(e.data)));
        es.addEventListener('vehicle_status', e => console.log(JSON.parse(e.data)));
    """
    queue = await sse_mgr.subscribe(username, filter_devNo=devNo)

    async def event_generator():
        try:
            # 自动启动 iotsmart WS（幂等）
            try:
                import time as _time
                ready = await DriverMonitorService.ensure_iotsmart_ws_connected()
                if ready is True:
                    # 只推该设备的在线状态
                    snapshot = DriverMonitorService.get_online_vehicle_snapshot()
                    dev_snapshot = [v for v in snapshot if str(v.get("devNo")) == devNo or str(v.get("vehicleNo")) == devNo]
                    if dev_snapshot:
                        msg = sse_mgr._build_message(
                            {"data": dev_snapshot, "timestamp": int(_time.time() * 1000)},
                            event="vehicle_online_list",
                        )
                        await queue.put(msg)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"[SSE初始化] 启动WS失败: {e}")

            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=25)
                    yield payload
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
        finally:
            await sse_mgr.unsubscribe(username, queue)

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_generator(), headers=headers)
