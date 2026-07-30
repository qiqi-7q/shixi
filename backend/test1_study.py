import time
from datetime import datetime
from app.core.aiohttp_client import get_session, close_session
import hashlib
import asyncio
import json
import aiohttp
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
##########################################################################################
########################## 轨迹回放
######## 历史定位数据
TRACK_URL = "/info_report/v1/query_realtime_data"
# 查询单页轨迹数据
async def query_track_page(
    session: ClientSession,
    token: str,
    vehicle_no: str,
    start_time: str,
    end_time: str,
    cur_page: int = 1,
    page_num: int = 100,
):
    """查询单页轨迹数据"""
    url = f"{BASIC_URL}{TRACK_URL}"
    headers = build_headers(token)
    params = {
        "startTime": start_time,
        "endTime": end_time,
        "vehicleNo": vehicle_no,
        "curPage": cur_page,
        "pageNum": page_num,
        "_t": int(time.time() * 1000),   # 如果不带 _t ，浏览器或中间代理可能把同一个 URL 的响应缓存起来，导致你第二次请求拿到的是旧数据。
    }
    response = await session.get(url, params=params, headers=headers)
    return await response.json()

# 查询全部轨迹数据
async def query_track_all(
    session: ClientSession,
    token: str,
    vehicle_no: str,
    start_time: str,
    end_time: str,
    page_num: int = 100,
):
    """分页查询全部轨迹数据，返回完整 dataList 列表"""
    all_points = []
    cur_page = 1

    while True:
        result = await query_track_page(
            session, token, vehicle_no, start_time, end_time, cur_page, page_num
        )

        biz = result.get("hdr", {})
        if biz.get("code") != 200:
            logger.error(f"[轨迹查询] 接口返回错误: {biz}")
            break

        data = result.get("data", {})
        points = data.get("dataList", [])
        total = data.get("total", 0)
        all_points.extend(points)

        logger.info(f"[轨迹查询] page={cur_page}, 本页{len(points)}条, 累计{len(all_points)}/{total}条")

        if len(all_points) >= total or not points:
            break
        cur_page += 1

    # 按定位时间升序排序，确保轨迹时间线正确
    all_points.sort(key=lambda p: p.get("time", 0))
    return all_points

##########################################################################################
##### 最后位置查询接口
LAST_VEHICLE_STATUS_URL = "/web_api/v1/realtime/last_vehicle_status_data"
async def get_last_vehicle_status(session: ClientSession, token: str):
    """获取用户所有车辆的最后状态（包含最后定位数据）

    该接口不需要额外参数，token 放在 Authorization 头中即可。
    """
    url = f"{BASIC_URL}{LAST_VEHICLE_STATUS_URL}"
    headers = build_headers(token)
    params = {
        "_t": int(time.time() * 1000),
    }
    response = await session.get(url, params=params, headers=headers)
    return await response.json()


async def get_vehicle_last_position(session: ClientSession, token: str, vehicle_no: str):
    """获取指定车辆的最后位置

    Args:
        session: aiohttp ClientSession
        token: 登录后获取的 token
        vehicle_no: 车辆编号/车牌号

    Returns:
        dict: 包含最后定位数据的字典，若未找到则返回 None
    """
    result = await get_last_vehicle_status(session, token)
    data_list = result.get("data", [])

    for item in data_list:
        last_gps = item.get("lastGpsData", {})
        if last_gps.get("devNo") == vehicle_no or item.get("vehicleNo") == vehicle_no:
            logger.info(f"[最后位置] vehicleNo={vehicle_no}, 位置={last_gps}")
            return last_gps

    logger.warning(f"[最后位置] 未找到 vehicleNo={vehicle_no} 的最后位置")
    return None
##########################################################################################
##### 终端重启
RESTART_URL = "/web_api/v1/dev_manage/device_reboot"
async def device_reboot(session: ClientSession, token: str, vehicle_nos: list):
    """终端重启（支持批量）

    Args:
        session: aiohttp ClientSession
        token: 登录后获取的 token
        vehicle_nos: 车牌号列表，如 ["527086498786", "527086468243"]

    Returns:
        dict: 返回结果，hdr.code=200表示下发成功，data是失败车牌号列表（空列表表示全部成功）
    """
    url = f"{BASIC_URL}{RESTART_URL}"
    headers = build_headers(token)
    headers["Content-Type"] = "application/json"
    body = {
        "vehicleNos": vehicle_nos,
    }
    response = await session.post(url, json=body, headers=headers)
    result = await response.json()

    hdr = result.get("hdr", {})
    failed_list = result.get("data", [])
    if hdr.get("code") == 200:
        if not failed_list:
            logger.info(f"[终端重启] 下发成功，所有车辆重启成功: {vehicle_nos}")
        else:
            logger.warning(f"[终端重启] 下发成功，但部分车辆重启失败: {failed_list}")
    else:
        logger.error(f"[终端重启] 下发失败: {hdr}")
    return result


async def restart_vehicle(session: ClientSession, token: str, vehicle_no: str):
    """重启单台车辆（便捷方法）"""
    return await device_reboot(session, token, [vehicle_no])

##########################################################################################
##### 文本下发
TEXT_URL = "/web_api/v1/dev_manage/send_text"
async def device_text(session: ClientSession, token: str, vehicle_nos: list, text: str, flag: int = None, task_name: str = None):
    """下发文本到终端（支持批量）

    Args:
        session: aiohttp ClientSession
        token: 登录后获取的 token
        vehicle_nos: 车牌号列表，如 ["527086498786", "527086468243"]
        text: 要下发的文本内容
        flag: 标志位，可选。2=紧急, 3=TTS, 4=广告屏显示，可组合
        task_name: 任务名称，可选

    Returns:
        dict: 返回结果，hdr.code=200表示下发成功，data是失败车牌号列表（空列表表示全部成功）
    """
    url = f"{BASIC_URL}{TEXT_URL}"
    headers = build_headers(token)
    headers["Content-Type"] = "application/json"
    body = {
        "vehicleNos": vehicle_nos,
        "text": text,
    }
    if flag is not None:
        body["flag"] = flag
    if task_name is not None:
        body["taskName"] = task_name
    response = await session.post(url, json=body, headers=headers)
    result = await response.json()

    hdr = result.get("hdr", {})
    failed_list = result.get("data", [])
    if hdr.get("code") == 200:
        if not failed_list:
            logger.info(f"[文本下发] 下发成功，所有车辆下发成功: {vehicle_nos}, text={text}")
        else:
            logger.warning(f"[文本下发] 下发成功，但部分车辆下发失败: {failed_list}")
    else:
        logger.error(f"[文本下发] 下发失败: {hdr}")
    return result


TRANS_MSG_URL = "/web_api/v1/dev_manage/send_trans_msg"
async def send_trans_msg(
    session: ClientSession,
    token: str,
    vehicle_nos: list,
    trans_type: int,
    trans_data: str,
    task_name: str = None,
):
    """JT808 自定义透传指令下发

    透传自定义终端指令，适配拓展下发需求，支持批量下发。

    Args:
        session: aiohttp ClientSession
        token: 登录后获取的 token
        vehicle_nos: 车牌号列表，如 ["527086498786", "527086468243"]
        trans_type: 透传类型（如 117，具体值按协议文档）
        trans_data: 透传数据（十六进制字符串或明文，按协议要求）
        task_name: 任务名称（可选）

    Returns:
        dict: data 为失败车牌号列表，空列表表示全部成功
    """
    url = f"{BASIC_URL}{TRANS_MSG_URL}"
    headers = build_headers(token)
    headers["Content-Type"] = "application/json"

    body = {
        "transType": trans_type,
        "transData": trans_data,
        "vehicleNos": vehicle_nos,
    }
    if task_name is not None:
        body["taskName"] = task_name

    response = await session.post(url, json=body, headers=headers)
    result = await response.json()

    hdr = result.get("hdr", {})
    if hdr.get("code") == 200:
        failed_list = result.get("data", [])
        if not failed_list:
            logger.info(f"[透传下发] 下发成功，所有车辆下发成功: {vehicle_nos}, transType={trans_type}")
        else:
            logger.warning(f"[透传下发] 下发成功，但部分车辆下发失败: {failed_list}")
    else:
        logger.error(f"[透传下发] 下发失败: {hdr}")
    return result


GET_DEV_PARAM_URL = "/web_api/v1/dev_manage/get_dev_param"
async def get_dev_param(
    session: ClientSession,
    token: str,
    vehicle_no: str,
    param_ids: str = None,
):
    """查询终端参数

    查询部标终端参数，包括视频相关参数。

    Args:
        session: aiohttp ClientSession
        token: 登录后获取的 token
        vehicle_no: 车牌号
        param_ids: 参数 ID 列表，空表示查所有，查询多个用逗号隔开（如 "1,16"）

    Returns:
        dict: data 为参数列表，每个元素包含 paramID/paramType/paramContent
              paramType: 2=4字节整型, 3=字符串
    """
    url = f"{BASIC_URL}{GET_DEV_PARAM_URL}"
    headers = build_headers(token)

    params = {
        "vehicleNo": vehicle_no,
        "_t": int(time.time() * 1000),
    }
    if param_ids is not None:
        params["paramIDs"] = param_ids

    response = await session.get(url, params=params, headers=headers)
    return await response.json()


SET_DEV_PARAM_URL = "/web_api/v1/dev_manage/set_dev_param"
async def set_dev_param(
    session: ClientSession,
    token: str,
    vehicle_nos: list,
    items: list,
):
    """设置终端参数

    批量设置部标终端参数，包括视频相关参数。

    Args:
        session: aiohttp ClientSession
        token: 登录后获取的 token
        vehicle_nos: 车牌号列表，如 ["527086498786"]
        items: 参数项列表，每个元素为 dict，格式：
               [
                 {"paramID": 1, "paramType": 2, "paramContent": "70"},
                 {"paramID": 117, "paramType": 4, "paramContent": "{...}"}
               ]
               paramType: 2=4字节整型, 3=字符串, 4=JSON对象字符串

    Returns:
        dict: data 为失败车牌号列表，空列表表示全部成功
    """
    url = f"{BASIC_URL}{SET_DEV_PARAM_URL}"
    headers = build_headers(token)
    headers["Content-Type"] = "application/json"

    body = {
        "vehicleNos": vehicle_nos,
        "items": items,
        "_t": int(time.time() * 1000),
    }

    response = await session.post(url, json=body, headers=headers)
    result = await response.json()

    hdr = result.get("hdr", {})
    if hdr.get("code") == 200:
        failed_list = result.get("data", [])
        if not failed_list:
            logger.info(f"[设置终端参数] 设置成功，所有车辆设置成功: {vehicle_nos}")
        else:
            logger.warning(f"[设置终端参数] 设置成功，但部分车辆设置失败: {failed_list}")
    else:
        logger.error(f"[设置终端参数] 设置失败: {hdr}")
    return result

##########################################################################################
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

LOCATION_FILE = "location_data.json"   # 定位数据文件名
LOCATION_INTERVAL = 30  # 定位数据写入文件的时间间隔，秒
_last_location_write_time = 0  # 上次写入时间戳


def save_location_to_file(data):
    """每隔30秒把定位数据追加写入JSON文件"""
    global _last_location_write_time
    now = time.time()
    if now - _last_location_write_time < LOCATION_INTERVAL:
        return
    _last_location_write_time = now

    try:
        with open(LOCATION_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []

    existing.append({"saveTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "data": data})

    with open(LOCATION_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)



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
                    save_location_to_file(data)
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
        connector=TCPConnector(limit=5, ssl=False),
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

##########################################################################################

async def main():

    vehicle_no = "527086498786"
    start_time = "2026-07-17 14:00:00"
    end_time = "2026-07-17 16:30:00"

    session = await get_session()
    try:
        user_name = "ZJLPKJ"
        password = "123456"
        password_md5 = hashlib.md5(password.encode()).hexdigest().lower()
        token, _ = await login(session, user_name, password_md5)

        # 1. 先查询车辆列表
        print("=" * 60)
        print("1. 查询车辆列表")
        print("=" * 60)
        car_info = await get_car_info(session, token)
        print(json.dumps(car_info, indent=2, ensure_ascii=False))

        # 2. 查询轨迹
        print("=" * 60)
        print("2. 查询轨迹")
        print("=" * 60)
        points = await query_track_all(session, token, vehicle_no, start_time, end_time)
        print(f"共获取 {len(points)} 个轨迹点")
        for p in points[:3]:
            print(p)

        # 3. 查询最后位置
        print("=" * 60)
        print("3. 查询最后位置")
        print("=" * 60)
        last_pos = await get_vehicle_last_position(session, token, vehicle_no)
        # last_status = await get_last_vehicle_status(session, token)
        print(json.dumps(last_pos, indent=2, ensure_ascii=False))
        # print(json.dumps(last_status, indent=2, ensure_ascii=False))

        # 4. 终端重启
        print("=" * 60)
        print("4. 终端重启")
        print("=" * 60)
        reboot_result = await restart_vehicle(session, token, vehicle_no)
        print(json.dumps(reboot_result, indent=2, ensure_ascii=False))

        # 5. 下发文本
        print("=" * 60)
        print("5. 下发文本")
        print("=" * 60)
        text_result = await device_text(
            session, token,
            vehicle_nos=[vehicle_no],
            text="测试文本下发",
            flag=3,
            task_name="测试任务"
        )
        print(json.dumps(text_result, indent=2, ensure_ascii=False))

        # 6. JT808 自定义透传指令下发
        print("=" * 60)
        print("6. JT808 自定义透传指令下发")        
        print("=" * 60)
        trans_result = await send_trans_msg(
            session, token,
            vehicle_nos=[vehicle_no],
            trans_type=117,
            trans_data="test",
            task_name="透传测试任务"
        )
        print(json.dumps(trans_result, indent=2, ensure_ascii=False))

        # 7. 查询终端参数
        print("=" * 60)
        print("7. 查询终端参数")
        print("=" * 60)
        param_result = await get_dev_param(session, token, vehicle_no, param_ids="1,16")
        print(json.dumps(param_result, indent=2, ensure_ascii=False))

        # 8. 设置终端参数（心跳间隔改为60秒）
        print("=" * 60)
        print("8. 设置终端参数")        
        print("=" * 60)
        set_param_items = [
            {"paramID": 1, "paramType": 2, "paramContent": "60"},
        ]
        set_result = await set_dev_param(session, token, [vehicle_no], set_param_items)
        print(json.dumps(set_result, indent=2, ensure_ascii=False))

        # 9. 启动WebSocket监听（会一直运行，按Ctrl+C停止）
        print("=" * 60)
        print("9. 启动WebSocket监听（按Ctrl+C停止）")
        print("=" * 60)
        await ws_login()

    finally:
        await close_session()


if __name__ == "__main__":
    asyncio.run(main())