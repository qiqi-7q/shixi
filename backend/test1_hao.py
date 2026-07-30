import time
from datetime import datetime, timedelta
from app.core.aiohttp_client import get_session, close_session
import hashlib
import asyncio
import json
from aiohttp import WSMsgType, ClientSession, TCPConnector, ClientTimeout
from app.core.redis_client import redisserve
from app.utils.logger import get_logger

logger = get_logger(__name__, log_filename="driver_monitor.log")

BASIC_URL = "http://pro.iotsmart.net"
WS_URL = "ws://pro.iotsmart.net"


# 构建请求头
def build_headers(token):
    return {
        "Authorization": f"Bearer {token}",
    }


LOGIN_URL = "/basic_api/v1/login"
async def login(session, userName: str, password_md5: str):
# async def login(userName: str, password_md5: str):
    """登录，获取token和deadTime。优先从Redis缓存读取，过期或即将过期时重新请求。"""
    # session = await get_session()
    # 从redis获取token和deadTime
    redis_data = await redisserve.get_data(f"iotsmart:token:{userName}")
    if redis_data:
        redis_data = redis_data.decode() if isinstance(redis_data, bytes) else redis_data
        token, dead_time = redis_data.rsplit("+", 1)
        dead_time = int(dead_time)
        # token未过期且未即将过期，直接返回缓存; 否则提前3分钟重新请求登录
        if time.time() + 3 * 60 < dead_time:
            logger.info(f"[登录] 从Redis缓存获取token, 过期时间: {datetime.fromtimestamp(dead_time).strftime('%Y-%m-%d %H:%M:%S')}")
            return token, dead_time
        
    url = f"{BASIC_URL}{LOGIN_URL}"
    payload = {
        "userName": userName,
        "password": password_md5,
        "_t": int(time.time() * 1000),
    }
    response = await session.get(url, params=payload)
    login_response = await response.json()
    
    token = login_response["data"]["token"]
    dead_time = login_response["data"]["deadTime"]  # 10小时有效期
    # 存储token到redis, 过期时间为deadTime - 当前时间
    await redisserve.set_data(f"iotsmart:token:{userName}", f"{token}+{dead_time}", dead_time - int(time.time()))
    logger.info(f"[登录] 从服务器获取token, 过期时间: {datetime.fromtimestamp(dead_time).strftime('%Y-%m-%d %H:%M:%S')}")
    return token, dead_time


GET_USER_ORG = "/basic_api/v1/org/get_user_org"
async def get_user_org(session, token: str):
    """获取用户分组信息"""
    url = f"{BASIC_URL}{GET_USER_ORG}"
    # token放在Authorization头中, 格式为: Bearer token
    headers = build_headers(token)
    payload = {
        "_t": int(time.time() * 1000),
    }
    response = await session.get(url, params=payload, headers=headers)
    return await response.json()


GET_CAR_INFO = "/basic_api/v1/user/get_user_vehicle_info_base_info"
async def get_car_info(session, token: str):
    """获取用户车辆基础信息"""
    url = f"{BASIC_URL}{GET_CAR_INFO}"
    # token放在Authorization头中, 格式为: Bearer token
    headers = build_headers(token)
    payload = {
        "_t": int(time.time() * 1000),
    }
    response = await session.get(url, params=payload, headers=headers)
    return await response.json()


GET_WS_INFO = "/web_api/v1/common/get_websocket_info"
async def get_ws_info(session, token: str):
    """获取websocket的服务器信息"""
    url = f"{BASIC_URL}{GET_WS_INFO}"
    # token放在Authorization头中, 格式为: Bearer token
    headers = build_headers(token)
    payload = {
        "_t": int(time.time() * 1000),
    }
    response = await session.get(url, params=payload, headers=headers)
    return await response.json()


REALTIME_AUDIO_URL = "/web_api/v1/media/realtime_audio_video"
async def get_realtime_audio(token: str, vehicleId: str):
    """3.3.1.实时流 打开视频"""
    session = await get_session()
    url = f"{BASIC_URL}{REALTIME_AUDIO_URL}"
    # token放在Authorization头中, 格式为: Bearer token
    headers = build_headers(token)
    payload = {
        "vehicleNo": vehicleId,
        "channelNo": 2,
        "isSubCode": 1,
        "dataType": 0,
        "_t": int(time.time() * 1000),
    }
    response = await session.get(url, params=payload, headers=headers)
    return await response.json()


REALTIME_MONITOR = "/web_api/v1/media/realtime_audio"
async def get_realtime_monitor(token: str, vehicleId: str):
    """3.3.2.实时流 监听"""
    session = await get_session()
    url = f"{BASIC_URL}{REALTIME_MONITOR}"
    # token放在Authorization头中, 格式为: Bearer token
    headers = build_headers(token)
    payload = {
        "vehicleNo": vehicleId,
        "channelNo": 2,
        "_t": int(time.time() * 1000),
    }
    response = await session.get(url, params=payload, headers=headers)
    return await response.json()


REALTIME_TALK = "/web_api/v1/media/realtime_talk"
async def get_realtime_talk(token: str, vehicleId: str):
    """3.3.3.实时流 对讲"""
    session = await get_session()
    url = f"{BASIC_URL}{REALTIME_TALK}"
    # token放在Authorization头中, 格式为: Bearer token
    headers = build_headers(token)
    payload = {
        "vehicleNo": vehicleId,
        "channelNo": 2,
        "playerProtocol": 2,
        "_t": int(time.time() * 1000),
    }
    response = await session.get(url, params=payload, headers=headers)
    return await response.json()


MEDIA_LIST = "/web_api/v1/media/get_media_list"
async def get_media_list(token: str, vehicleId: str, startTime: str, endTime: str, alarmFlag: int = None, mediaType: int = None, bitStreamType: int = None, storageType: int = None):
    """3.3.4.获取媒体列表"""
    session = await get_session()
    # startTime和endTime格式为datetime格式转的str，现在需要把它们转换为UTC时间戳，不用mktime
    starttime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
    endtime = datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")
    url = f"{BASIC_URL}{MEDIA_LIST}"
    # token放在Authorization头中, 格式为: Bearer token 
    headers = build_headers(token)
    payload = {
        "vehicleNo": vehicleId,
        "channelNo": 2,
        "startTime": int(starttime.timestamp()),  # UTC时间戳
        "endTime": int(endtime.timestamp()),  
        "_t": int(time.time() * 1000),
    }
    if alarmFlag:
        payload["alarmFlag"] = alarmFlag
    if mediaType:
        payload["mediaType"] = mediaType
    if bitStreamType:
        payload["bitStreamType"] = bitStreamType
    if storageType:
        payload["storageType"] = storageType
    response = await session.get(url, params=payload, headers=headers)
    return await response.json()


HISTORY_VIDEO = "/web_api/v1/media/history_video"
async def get_history_video(token: str, vehicleId: str, startTime: str, endTime: str, playType: int = None, mediaType: int = None, speed: int = None, storageType: int = None, isDownload: int = None, isSubCode: int = None):
    """3.3.2.5.请求历史流"""
    session = await get_session()
    # startTime和endTime格式为datetime格式转的str，现在需要把它们转换为UTC时间戳，不用mktime
    starttime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
    endtime = datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")
    url = f"{BASIC_URL}{HISTORY_VIDEO}"
    # token放在Authorization头中, 格式为: Bearer token 
    headers = build_headers(token)
    payload = {
        "vehicleNo": vehicleId,
        "channelNo": 2,
        "startTime": int(starttime.timestamp()),  # UTC时间戳
        "endTime": int(endtime.timestamp()),  
        "_t": int(time.time() * 1000),
    }
    if isSubCode:
        payload["isSubCode"] = isSubCode
    if mediaType:
        payload["mediaType"] = mediaType
    if storageType:
        payload["storageType"] = storageType
    if playType:
        payload["playType"] = playType
    if speed:
        payload["speed"] = speed
    if isDownload:
        payload["isDownload"] = isDownload

    response = await session.get(url, params=payload, headers=headers)
    return await response.json()


CTRL_HISTORY_VIDEO = "/web_api/v1/media/ctrl_history_video"
async def ctrl_history_video(token: str, vehicleId: str, ctrlType: int = None, speed: int = None, dragTime: str = None):
    """回放控制"""
    session = await get_session()
    dragtime = datetime.strptime(dragTime, "%Y-%m-%d %H:%M:%S")
    url = f"{BASIC_URL}{CTRL_HISTORY_VIDEO}"
    # token放在Authorization头中, 格式为: Bearer token 
    headers = build_headers(token)
    payload = {
        "vehicleNo": vehicleId,
        "channelNo": 2,
        "_t": int(time.time() * 1000),
    }
    if ctrlType:
        payload["ctrlType"] = ctrlType
    if speed:
        payload["speed"] = speed
    if dragTime:
        payload["dragTime"] = int(dragtime.timestamp())

    response = await session.get(url, params=payload, headers=headers)
    return await response.json()


PLAYBACK_TIME = "/web_api/v1/media/get_playback_time"
async def get_playback_time(token: str, zlmStreamID: str):
    """3.3.2.13.获取历史流播放进度"""
    session = await get_session()
    url = f"{BASIC_URL}{PLAYBACK_TIME}"
    # token放在Authorization头中, 格式为: Bearer token 
    headers = build_headers(token)
    payload = {
        "zlmStreamID":zlmStreamID,
        "_t": int(time.time() * 1000),
    }
    response = await session.get(url, params=payload, headers=headers)
    return await response.json()



WS_LOGIN_URL = "/web_session"
HEARTBEAT_INTERVAL = 30  # 心跳间隔30秒
# WebSocket消息类型定义
MSG_TYPE_VEHICLE_ONLINE_LIST_FIRST = 800  # 车辆在线列表（连接后首推）
MSG_TYPE_HEARTBEAT_REQ = 1001             # 心跳保持-请求
MSG_TYPE_HEARTBEAT_RESP = 5001            # 心跳保持-应答
MSG_TYPE_VEHICLE_ONLINE_LIST = 8000       # 车辆在线列表（后续推送）
MSG_TYPE_VEHICLE_ON_OFF = 8001            # 车辆上下线推送
MSG_TYPE_LOCATION = 8002                  # 定位数据推送
MSG_TYPE_ALARM = 8003                     # 报警数据推送
MSG_TYPE_ATTACHMENT = 8004                # 附件信息推送
MSG_TYPE_ATTACHMENT_8005 = 8005           # 附件信息推送

async def ws_heartbeat(ws, stop_event):
    """定时发送心跳消息"""
    req_sn = 1
    while not stop_event.is_set():
        heartbeat_msg = {
            "hdr": {
                "message": "",
                "msgType": MSG_TYPE_HEARTBEAT_REQ,
                "reqSN": req_sn,
                "respSN": 0
            }
        }
        await ws.send_json(heartbeat_msg)
        logger.info(f"[心跳发送] reqSN={req_sn}")
        req_sn += 1
        await asyncio.sleep(HEARTBEAT_INTERVAL)

async def ws_receive(ws, stop_event):
    """接收服务器消息并按 msgType 分类处理"""
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:  # 文本消息
                data = json.loads(msg.data)
                msg_type = data.get("hdr", {}).get("msgType")
                if msg_type == MSG_TYPE_VEHICLE_ONLINE_LIST_FIRST:
                    logger.info(f"[车辆在线列表-首推] {data}")
                elif msg_type == MSG_TYPE_HEARTBEAT_RESP:
                    logger.info(f"[心跳响应] {data}")
                elif msg_type == MSG_TYPE_VEHICLE_ONLINE_LIST:
                    logger.info(f"[车辆在线列表] {data}")
                elif msg_type == MSG_TYPE_VEHICLE_ON_OFF:
                    logger.info(f"[车辆上下线] {data}")
                elif msg_type == MSG_TYPE_LOCATION:
                    logger.info(f"[定位数据] {data}")
                elif msg_type == MSG_TYPE_ALARM:
                    logger.info(f"[报警数据] {data}")
                elif msg_type in (MSG_TYPE_ATTACHMENT, MSG_TYPE_ATTACHMENT_8005):
                    logger.info(f"[附件信息] {data}")
                else:
                    # 尝试断开websocket连接并重新连接
                    logger.info(f"[未知消息类型 {msg_type}] {data}")
                    stop_event.set()
                    break
            elif msg.type == WSMsgType.CLOSE:  # 关闭消息
                logger.info("[WebSocket] 服务器关闭连接")
                break
            elif msg.type == WSMsgType.BINARY:  # 二进制消息
                logger.info("[WebSocket] 收到二进制消息")
                # 解析二进制数据
                try:
                    binary_data = json.loads(msg.data.decode())
                    logger.info(f"[解析后的二进制数据] {binary_data}")
                except json.JSONDecodeError:
                    logger.info("[二进制数据解析错误] 不是有效JSON格式")
            elif msg.type == WSMsgType.CLOSED:  # 已关闭消息
                logger.info("[WebSocket] 连接已关闭")
                break
            elif msg.type == WSMsgType.CLOSING:  # 关闭中消息
                logger.info("[WebSocket] 服务器关闭连接中")
                break
            elif msg.type == WSMsgType.ERROR:  # 错误
                logger.info(f"[WebSocket] 错误: {msg.data}")
                break
    except Exception as e:
        logger.info(f"[接收异常] {e}")

async def ws_login():
    """websocket连接登录并保持心跳"""
    # HTTP 请求用全局 session（有20秒超时，适合短请求）
    http_session = await get_session()
    # WebSocket 用独立 session（无总超时，适合长连接）
    ws_session = ClientSession(
        connector=TCPConnector(limit=5, verify_ssl=False),
        timeout=ClientTimeout(total=None)  # 关闭总超时
    )

    userName = "ZJLPKJ"
    password = "123456"
    password_md5 = hashlib.md5(password.encode()).hexdigest().lower()

    try:
        url = f"{WS_URL}{WS_LOGIN_URL}"
        reconnect_delay = 1
        max_reconnect_delay = 30

        while True:
            try:
                # 每次连接前通过login获取token（Redis缓存，不过期不重复请求）
                platform_token, deadTime = await login(http_session, userName, password_md5)
                logger.info(f"[登录成功] token: {platform_token}, deadTime: {deadTime}")
                
                payload = {"token": platform_token}
                async with ws_session.ws_connect(url, params=payload) as ws:
                    # 接收登录响应
                    login_msg = await ws.receive()
                    logger.info(f"[登录响应] {login_msg.data}")

                    # 重置重连延迟
                    reconnect_delay = 1

                    # 启动心跳和接收任务
                    stop_event = asyncio.Event()

                    heartbeat_task = asyncio.create_task(ws_heartbeat(ws, stop_event))
                    receive_task = asyncio.create_task(ws_receive(ws, stop_event))

                    # 等待任一任务完成
                    done, pending = await asyncio.wait(
                        [heartbeat_task, receive_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )

                    # 取消未完成的任务并等待结束
                    for task in pending:
                        task.cancel()
                    if pending:
                        await asyncio.gather(*pending, return_exceptions=True)

            except asyncio.CancelledError as e:
                logger.info(f"[任务取消] {e}")
                break
            except Exception as e:
                logger.info(f"[连接异常] {e}，{reconnect_delay}秒后重连")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
    finally:
        # 确保 WebSocket session 被关闭
        if ws_session and not ws_session.closed:
            await ws_session.close()
            logger.info("[WebSocket Session已关闭]")
        # 关闭全局 HTTP session
        await close_session()
        logger.info("[HTTP Session已关闭]")


if __name__ == "__main__":

    # userName = "ZJLPKJ"
    # password = "123456"
    # password_md5 = hashlib.md5(password.encode()).hexdigest().lower()

    async def main():
        await ws_login()
        
        # token, deadTime = await login(userName, password_md5)
        
        # data = await get_realtime_audio(token, "527086498786")
        # logger.info(f"[实时流打开视频] {data}")
        
        # data = await get_realtime_monitor(token, "527086498786")
        # logger.info(f"[实时流打开音频] {data}")
        
        # data = await get_realtime_talk(token, "527086498786")
        # logger.info(f"[实时流打开对讲] {data}")
        
        # now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # # 1小时前
        # one_hour_ago = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        # data = await get_media_list(token, "527086498786", one_hour_ago, now_time, alarmFlag=0, mediaType=3, bitStreamType=0, storageType=0)
        # 解析返回的JSON数据
        # media_list = data.get("data", {})
        # for item in media_list:
        #     fileSize = item.get("fileSize") / 1024 / 1024  # 转换为MB
        #     startTime = datetime.fromtimestamp(item.get("startTime")).strftime("%Y-%m-%d %H:%M:%S")
        #     endTime = datetime.fromtimestamp(item.get("endTime")).strftime("%Y-%m-%d %H:%M:%S")
        #     logger.info("通道:", item.get("channelNo"),"开始时间:", startTime,"结束时间:", endTime,"文件大小:", f"{fileSize:.0f} MB")
        
        # data = await get_history_video(token, "527086498786", one_hour_ago, now_time, playType=0, mediaType=0, speed=1, storageType=1, isDownload=0, isSubCode=1)
        # logger.info(f"[获取历史流] {data}")
        
        # data = await ctrl_history_video(token, "527086498786", ctrlType=5, speed=1, dragTime=now_time)
        # logger.info(f"[回放控制] {data}")
        
        # data = await get_playback_time(token, "7297425653840742156")
        # logger.info(f"[获取历史流播放进度] {data}")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n[用户中断] 程序退出")
