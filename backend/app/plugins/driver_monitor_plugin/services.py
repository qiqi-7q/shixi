from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query
from app.core.database import get_db, SessionLocal
from app.plugins.driver_monitor_plugin import models, schemas, services
from app.core.config import settings
import asyncio

import time
import hashlib
import os
import json
from app.core.aiohttp_client import get_session
from aiohttp import WSMsgType, ClientSession, TCPConnector, ClientTimeout
from app.utils.logger import get_logger
from app.core.redis_client import redisserve
from sqlalchemy import select
from sqlalchemy import func
from app.core.sse_client import sse_mgr
from app.core.minio_client import minioserve


logger = get_logger(__name__, log_filename="driver_monitor.log")
ws_logger = get_logger("driver_monitor.ws", log_filename="driver_monitor.log")

# 智驾车联网平台 API Base_URL
BASIC_URL = settings.MONITOR_BASIC_URL
# 智驾车联网平台 WebSocket URL
WS_URL = settings.MONITOR_WS_URL
# 智驾车联网平台 用户名 密码 密码MD5
userName = settings.MONITOR_USERNAME
password = settings.MONITOR_PASSWORD
password_md5 = hashlib.md5(password.encode()).hexdigest().lower()

# 报警类型映射表
ALARM_INFO_MAP = {
    "1": "疲劳驾驶", "2": "打电话", "3": "抽烟", "4": "分神", "5": "驾驶员异常",
    "6": "自动抓拍", "7": "驾驶员变更事件", "20": "向前碰撞", "21": "车道偏离报警",
    "22": "车距过近报警", "23": "行人碰撞报警", "24": "频繁变道报警", "25": "道路标识超限报警",
    "26": "障碍物报警", "27": "道路标识识别事件", "28": "主动抓拍事件", "35": "后方",
    "36": "左后方", "37": "右后方", "38": "急加速报警", "39": "急减速报警", "43": "胎压报警",
    "50": "超速", "51": "超时", "52": "GNSS模块异常", "53": "天线短路", "54": "天线未接",
    "55": "低电压异常", "56": "主电源掉电报警", "57": "TTS故障", "58": "IC卡故障",
    "59": "VSS故障", "60": "油量异常", "61": "非法点火", "62": "非法位移", "63": "非法开门",
    "64": "危险预警", "65": "紧急报警", "66": "车辆被盗", "67": "高温报警", "68": "通信模块异常",
    "70": "视频丢失", "71": "存储介质故障", "72": "视频遮挡", "100": "离线超时",
    "101": "进出围栏", "203": "点火抓拍", "204": "熄火抓拍", "205": "定时抓拍", "206": "碰撞抓拍",
}

# 智驾车联网平台 API 登录
LOGIN_URL = "/basic_api/v1/login"
# 智驾车联网平台 API 获取用户车辆基础信息
CAR_INFO = "/basic_api/v1/user/get_user_vehicle_info_base_info"
# 智驾车联网平台 API 实时视频
REALTIME_AUDIO_URL = "/web_api/v1/media/realtime_audio_video"
# 智驾联网平台 API 获取视频回放媒体列表
MEDIA_LIST = "/web_api/v1/media/get_media_list"
# 智驾联网平台 API 请求历史流
HISTORY_VIDEO = "/web_api/v1/media/history_video"
# 智驾联网平台 API 控制历史流
CTRL_HISTORY_VIDEO = "/web_api/v1/media/ctrl_history_video"
# 智驾联网平台 API 获取播放进度
PLAYBACK_TIME = "/web_api/v1/media/get_playback_time"
# 智驾联网平台 API 获取录像下载进度
DOWNLOAD_PROGRESS = "/web_api/v1/media/record_download_progress"
# 智驾联网平台 API 录像下载到本地   
FILE_DOWNLOAD = "/web_api/v1/media/record_file_download"
# 智驾联网平台 API 获取websocket的服务器信息
GET_WS_INFO = "/web_api/v1/common/get_websocket_info"
# 智驾车联网平台 API 获取用户分组信息
USER_ORG_URL = "/basic_api/v1/org/get_user_org"
# 智驾车联网平台 API 查询历史定位数据
TRACK_URL = "/info_report/v1/query_realtime_data"
# 智驾车联网平台 API 查询所有车辆最后状态
LAST_VEHICLE_STATUS_URL = "/web_api/v1/realtime/last_vehicle_status_data"
# 智驾车联网平台 API 终端重启
RESTART_URL = "/web_api/v1/dev_manage/device_reboot"
# 智驾车联网平台 API 文本下发
TEXT_URL = "/web_api/v1/dev_manage/send_text"
# 智驾车联网平台 API JT808 透传指令
TRANS_MSG_URL = "/web_api/v1/dev_manage/send_trans_msg"
# 智驾车联网平台 API 查询终端参数
GET_DEV_PARAM_URL = "/web_api/v1/dev_manage/get_dev_param"
# 智驾车联网平台 API 设置终端参数
SET_DEV_PARAM_URL = "/web_api/v1/dev_manage/set_dev_param"
# 智驾车联网平台 WebSocket 登录
WS_LOGIN_URL = "/web_session"
# 智驾联网平台 API 车辆上下线查询
QUERY_ONOFFLINE_DATA = "/info_report/v1/query_dev_onoffline_data"


# IoT 平台 API（从 source services.py 整合）
ALARM_DATA_URL = "/info_report/v1/query_alarm_data"
ATTACHMENT_INFO_URL = "/web_api/v1/media/get_attachment_info"



REALTIME_MONITOR_URL = "/web_api/v1/media/realtime_audio"
REALTIME_TALK_URL = "/web_api/v1/media/realtime_talk"
DOWNLOAD_STREAMID = "/web_api/v1/media/get_record_download_list"
DAILY_INFO = "/info_report/v1/query_vehicle_daily_info"




# WebSocket 配置
HEARTBEAT_INTERVAL = 30  # 心跳间隔秒
LOCATION_INTERVAL = 30  # 定位落盘间隔秒
LOCATION_MINIO_PREFIX = "test/driver_monitor/location"  # MinIO 存储前缀，按 devNo 分文件


# 每车每日上下线时长汇总文件（数组结构，便于后续迁移数据库）
_SUMMARY_FILE = os.path.join(settings.BASE_DIR, "static", "driver_monitor", "daily_summary.json")

# 车辆在线状态缓存（key: "guid:{id}"/"no:{车牌}"/"dev:{终端号}", value: dict 含isOnline等信息）
online_vehicle_cache = {}

# 标记是否已收到初始在线列表（8000消息）
_online_list_initialized = False

# WebSocket 消息类型
MSG_TYPE_VEHICLE_ONLINE_LIST_FIRST = 800
MSG_TYPE_HEARTBEAT_REQ = 1001
MSG_TYPE_HEARTBEAT_RESP = 5001
MSG_TYPE_VEHICLE_ONLINE_LIST = 8000
MSG_TYPE_VEHICLE_ON_OFF = 8001
MSG_TYPE_LOCATION = 8002
MSG_TYPE_ALARM = 8003
MSG_TYPE_ATTACHMENT = 8004
MSG_TYPE_ATTACHMENT_8005 = 8005

# 定位数据落盘时间戳
last_location_write_time = 0
# 缓存30秒内的所有定位点位
latest_points = []

# 智驾联网平台 API 状态码
status_codes = {
    10000: "通用错误",
    10001: "用户或者密码不对",
    10002: "token失效",
    10003: "输入参数有误",
    10004: "生成token失败",
    10005: "服务器内部出错",
    10006: "用户无权限",
    10007: "数据库操作失败",
    10008: "数据存在",
    10009: "数据不存在",
    10010: "旧密码不匹配",
    10011: "数量达到最大",
    10012: "端口分配不足",
    10013: "资源忙",
    10014: "终端离线",
    10015: "请求超时",
    10016: "服务不可用",
    10017: "终端不支持",
}
class DriverMonitorService:

        # ===================================平台接口=============================

    @staticmethod
    async def get_monitor_info(
        db: AsyncSession,
        vin_code: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        page: int = Query(1, ge=1, description="页码"),  # >=1
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> dict | tuple[int, str]:
        """获取用户车辆监控信息"""
        stmt = select(models.MonitorInfo)

        filters = []
        if vin_code:
            filters.append(models.MonitorInfo.vin_code == vin_code)
        if start_time:
            filters.append(models.MonitorInfo.test_date >= start_time)
        if end_time:
            filters.append(models.MonitorInfo.test_date <= end_time)

        stmt = stmt.where(*filters)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await db.scalar(count_stmt) or 0

        default_sort = "test_date"
        default_desc = True
        sort_expr = None

        # 处理空排序场景
        if not sort_by:
            sort_by = default_sort
            is_desc = default_desc
        else:
            # 字段白名单校验
            if sort_by not in schemas.MONITOR_WHITELIST:
                sort_by = default_sort
            # 校验排序方向,默认倒序排序
            valid_order = sort_order.lower() if sort_order else "desc"
            is_desc = (
                valid_order == "desc"
                if valid_order in ("asc", "desc")
                else default_desc
            )

        sort_expr = getattr(models.MonitorInfo, sort_by)

        # 升降序统一处理
        order_clause = sort_expr.desc() if is_desc else sort_expr.asc()
        stmt = (
            stmt.order_by(order_clause).offset((page - 1) * page_size).limit(page_size)
        )

        # 3. 查询逻辑全局只写一次，无重复
        result = await db.execute(stmt)
        data_list = list(result.scalars().all())
        return {
            "items": data_list,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_alarm_records(
        db: AsyncSession,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        alarm_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ):
        """分页查询报警记录"""
        stmt = select(models.AlarmRecord)
        count_stmt = select(func.count(models.AlarmRecord.id))

        if start_time:
            stmt = stmt.where(models.AlarmRecord.alarm_time >= start_time)
            count_stmt = count_stmt.where(models.AlarmRecord.alarm_time >= start_time)
        if end_time:
            stmt = stmt.where(models.AlarmRecord.alarm_time <= end_time)
            count_stmt = count_stmt.where(models.AlarmRecord.alarm_time <= end_time)
        if alarm_type:
            # 兼容数字编码（如 "1"）和中文（如 "疲劳驾驶"）两种查询方式
            alarm_type_cn = ALARM_INFO_MAP.get(alarm_type, alarm_type)
            stmt = stmt.where(models.AlarmRecord.alarm_type == alarm_type_cn)
            count_stmt = count_stmt.where(models.AlarmRecord.alarm_type == alarm_type_cn)

        stmt = stmt.order_by(models.AlarmRecord.alarm_time.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        total_result = await db.execute(count_stmt)
        total = total_result.scalar()

        result = await db.execute(stmt)
        records = result.scalars().all()

        records_data = []
        for r in records:
            records_data.append({
                "id": r.id,
                "alarm_id": r.alarm_id,
                "alarm_time": r.alarm_time.strftime("%Y-%m-%d %H:%M:%S") if r.alarm_time else None,
                "vin_code": r.vin_code,
                "alarm_type": r.alarm_type,
                "speed": r.speed,
                "remark": r.remark,
                "create_time": r.create_time.strftime("%Y-%m-%d %H:%M:%S") if r.create_time else None,
            })

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "records": records_data,
        }

    @staticmethod
    async def get_alarm_type_stats(
        db: AsyncSession,
        vin_code: str,
        target_date: Optional[date] = None,
    ):
        """统计指定车辆某天各报警类型的次数（默认当天）"""
        target_date = target_date or date.today()
        stmt = select(
            models.AlarmRecord.alarm_type,
            func.count(models.AlarmRecord.id).label("count"),
        ).where(
            models.AlarmRecord.vin_code == vin_code,
            func.date(models.AlarmRecord.alarm_time) == target_date,
        ).group_by(models.AlarmRecord.alarm_type).order_by(func.count(models.AlarmRecord.id).desc())

        result = await db.execute(stmt)
        rows = result.all()
        stats = [{"alarm_type": r[0], "count": r[1]} for r in rows]
        total = sum(item["count"] for item in stats)
        return {"vin_code": vin_code, "date": target_date, "total": total, "stats": stats}

    @staticmethod
    async def _save_alarm_to_db(body: dict):
        """将报警数据存入 alarm_records 表"""
        try:
            alarm_data_list = body.get("data", [])
            if not alarm_data_list:
                ws_logger.warning("[报警推送] 报警数据列表为空")
                return

            alarm_data = alarm_data_list[0]
            ws_logger.info(f"[报警推送] 开始处理入库: alarmType={alarm_data.get('alarmType')} alarmID={alarm_data.get('alarmID')}")

            alarm_time_raw = alarm_data.get("time", 0)
            alarm_time = datetime.fromtimestamp(alarm_time_raw) if alarm_time_raw else datetime.now()
            alarm_type_raw = str(alarm_data.get("alarmType", ""))
            alarm_type = ALARM_INFO_MAP.get(alarm_type_raw, alarm_data.get("alarmInfo", f"类型{alarm_type_raw}"))
            speed_raw = alarm_data.get("speed", 0)
            speed = Decimal(str(speed_raw)) / 10 if speed_raw else None
            vin_code = alarm_data.get("vehicleNo", "")
            remark = alarm_data.get("alarmInfo", "")


            async with SessionLocal() as session:
                record = models.AlarmRecord(
                    alarm_id=alarm_id,
                    alarm_time=alarm_time,
                    alarm_type=alarm_type,
                    speed=speed,
                    vin_code=vin_code,
                    remark=remark,
                )
                session.add(record)
                await session.commit()
                ws_logger.info(f"[报警推送] 报警数据已存入数据库: id={record.id} type={alarm_type}")
        except Exception as e:
            ws_logger.error(f"[报警推送] 存储报警数据异常: {e}", exc_info=True)



    # ===================================第三方平台接口=============================

    # 构建请求头
    @staticmethod
    def build_headers(token):
        return {
            "Authorization": f"Bearer {token}",
        }

    @staticmethod
    async def login() -> str | tuple[int, str]:
        """登录，获取token和deadTime。优先从Redis缓存读取，过期或即将过期时重新请求。"""
        session = await get_session()

        # 从redis获取token和deadTime
        redis_data = await redisserve.get_data(f"iotsmart:token:{userName}")
        if redis_data:
            redis_data = (
                redis_data.decode() if isinstance(redis_data, bytes) else redis_data
            )
            token, dead_time = redis_data.rsplit("+", 1)
            dead_time = int(dead_time)
            # token未过期且未即将过期，直接返回缓存; 否则提前3分钟重新请求登录
            if time.time() + 3 * 60 < dead_time:
                return token

            refresh_reason = "token过期或即将过期"
        else:
            refresh_reason = "Redis缓存中无token"

        logger.info(f"[登录] 需要刷新token, 原因: {refresh_reason}")

        # 加锁，确保只有一个请求登录，没抢到锁则等待后重试
        lock_key = f"lock:iotsmart:login:{userName}"
        client_id = await redisserve.acquire_lock(lock_key, 2)
        if not client_id:
            await asyncio.sleep(1)  # 等待1秒后重试
            logger.warning(f"[登录] 其他请求正在登录，稍后重试")
            return await DriverMonitorService.login()
        # 从服务器请求登录
        url = f"{BASIC_URL}{LOGIN_URL}"
        payload = {
            "userName": userName,
            "password": password_md5,
            "_t": int(time.time() * 1000),
        }
        request_start = time.perf_counter()
        try:
            response = await session.get(url, params=payload)
            login_response = await response.json()

            if login_response["hdr"]["code"] == 200:
                token = login_response["data"]["token"]
                dead_time = login_response["data"]["deadTime"]  # 10小时有效期
                expire_times = dead_time - int(time.time())
            else:
                error_str = "认证失败:" + status_codes.get(login_response["hdr"]["code"], "未知错误")
                return (login_response["hdr"]["code"], error_str)

            # 记录请求耗时和过期时间
            cost_ms = int((time.perf_counter() - request_start) * 1000)
            logger.info(f"[登录] 从服务器获取token成功, 耗时: {cost_ms}ms, 过期时间: {expire_times}s")

            # 存储token到redis, 过期时间为deadTime - 当前时间
            await redisserve.set_data(
                f"iotsmart:token:{userName}",
                f"{token}+{dead_time}",
                expire_times,
            )
            # dead_time从时间戳转为时间字符串
            dead_time_str = datetime.fromtimestamp(dead_time).strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[登录] 刷新token完成, 过期时间: {expire_times}s, dead_time: {dead_time_str}")

            return token
        except Exception as e:
            # 记录异常信息
            cost_ms = int((time.perf_counter() - request_start) * 1000)
            err_type = type(e).__name__
            logger.error(f"[登录] 从服务器获取token失败, 耗时: {cost_ms}ms, 异常类型: {err_type}, 错误信息: {str(e)}")
            raise
        finally:
            # 释放锁
            await redisserve.lua_script(lock_key, client_id)

    @staticmethod
    async def get_car_info():
        """获取用户车辆基础信息"""
        session = await get_session()
        url = f"{BASIC_URL}{CAR_INFO}"
        # token放在Authorization头中, 格式为: Bearer token
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        payload = {
            "_t": int(time.time() * 1000),
        }
        try:
            response = await session.get(url, params=payload, headers=headers)
            carinfo_json = await response.json()
        except Exception as e:
            return f"获取用户车辆基础信息失败, 错误信息: {str(e)}"
        if carinfo_json["hdr"]["code"] == 200:
            carinfo = carinfo_json["data"]
            return carinfo
        else:
            return status_codes.get(carinfo_json["hdr"]["code"], "未知错误")

    @staticmethod
    async def get_realtime_audio(vehicleNo: str, channelNo: int):
        session = await get_session()
        url = f"{BASIC_URL}{REALTIME_AUDIO_URL}"
        # token放在Authorization头中, 格式为: Bearer token
        token = await DriverMonitorService.login()

        if isinstance(token, tuple):
            return token[1]

        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {
            "vehicleNo": vehicleNo,
            "channelNo": channelNo,
            "isSubCode": "true",
            "dataType": 0,
            "_t": int(time.time() * 1000),
        }

        try:
            response = await session.get(url, params=payload, headers=headers)

            realtime_audio_json = await response.json()
        except Exception as e:
            return f"获取实时视频失败, 错误信息: {str(e)}"

        if (
            realtime_audio_json["hdr"]["code"]
            and realtime_audio_json["hdr"]["code"] == 200
        ):
            realtime_audio = realtime_audio_json["data"]
            return realtime_audio
        else:
            return status_codes.get(realtime_audio_json["hdr"]["code"], "未知错误")

    @staticmethod
    async def get_realtime_monitor(vehicleNo: str, channelNo: int):
        """实时音频监听"""
        session = await get_session()
        url = f"{BASIC_URL}{REALTIME_MONITOR_URL}"
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {
            "vehicleNo": vehicleNo,
            "channelNo": channelNo,
            "_t": int(time.time() * 1000),
        }
        try:
            response = await session.get(url, params=payload, headers=headers)
            realtime_monitor_json = await response.json()
        except Exception as e:
            return f"获取实时音频监听失败, 错误信息: {str(e)}"
        if realtime_monitor_json["hdr"]["code"] == 200:
            return realtime_monitor_json["data"]
        else:
            return status_codes.get(realtime_monitor_json["hdr"]["code"], "未知错误")

    @staticmethod
    async def get_realtime_talk(
        vehicleNo: str, channelNo: int, playerProtocol: int = 2
    ):
        """实时对讲"""
        session = await get_session()
        url = f"{BASIC_URL}{REALTIME_TALK_URL}"
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {
            "vehicleNo": vehicleNo,
            "channelNo": channelNo,
            "playerProtocol": playerProtocol,
            "_t": int(time.time() * 1000),
        }
        try:
            response = await session.get(url, params=payload, headers=headers)
            realtime_talk_json = await response.json()
        except Exception as e:
            return f"获取实时对讲失败, 错误信息: {str(e)}"
        if realtime_talk_json["hdr"]["code"] == 200:
            return realtime_talk_json["data"]
        else:
            return status_codes.get(realtime_talk_json["hdr"]["code"], "未知错误")

    @staticmethod
    async def get_media_list(
        vehicleNo: str,
        startTime: str,
        endTime: str,
        channelNo: Optional[int] = None,
        alarmFlag: Optional[int] = None,
        mediaType: Optional[int] = 3,
        bitStreamType: Optional[int] = 0,
        storageType: Optional[int] = 0,
    ):
        """视频回放 获取媒体列表"""
        session = await get_session()

        starttime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
        endtime = datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")
        url = f"{BASIC_URL}{MEDIA_LIST}"
        # token放在Authorization头中, 格式为: Bearer token
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {
            "vehicleNo": vehicleNo,
            "startTime": int(starttime.timestamp()),  # UTC时间戳
            "endTime": int(endtime.timestamp()),
            "_t": int(time.time() * 1000),
        }
        if channelNo:
            payload["channelNo"] = channelNo
        if alarmFlag:
            payload["alarmFlag"] = alarmFlag
        if mediaType:
            payload["mediaType"] = mediaType
        if bitStreamType:
            payload["bitStreamType"] = bitStreamType
        if storageType:
            payload["storageType"] = storageType
        try:
            response = await session.get(url, params=payload, headers=headers)
            media_list_json = await response.json()
        except Exception as e:
            return f"获取视频回放媒体列表失败, 错误信息: {str(e)}"
        if media_list_json["hdr"]["code"] == 200:
            media_list = media_list_json["data"]
            return media_list
        else:
            return status_codes.get(media_list_json["hdr"]["code"], "未知错误")

    @staticmethod
    async def get_history_video(
        vehicleNo: str,
        channelNo: int,
        startTime: str,
        endTime: str,
        playType: Optional[int] = 0,
        mediaType: Optional[int] = 0,
        speed: Optional[int] = 1,
        storageType: Optional[int] = 0,
        isDownload: Optional[bool] = None,
        isSubCode: Optional[bool] = True,
    ):
        """视频回放 请求历史流"""
        session = await get_session()
        starttime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
        endtime = datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")
        url = f"{BASIC_URL}{HISTORY_VIDEO}"
        # token放在Authorization头中, 格式为: Bearer token
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]

        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {
            "vehicleNo": vehicleNo,
            "channelNo": channelNo,
            "startTime": int(starttime.timestamp()),  # UTC时间戳
            "endTime": int(endtime.timestamp()),
            "_t": int(time.time() * 1000),
        }
        if isSubCode is not None:
            payload["isSubCode"] = "true" if isSubCode else "false"
        if mediaType is not None:
            payload["mediaType"] = mediaType
        if storageType is not None:
            payload["storageType"] = storageType
        if playType is not None:
            payload["playType"] = playType
        if speed is not None:
            payload["speed"] = speed
        if isDownload is not None:
            payload["isDownload"] = "true" if isDownload else "false"

        try:
            response = await session.get(url, params=payload, headers=headers)
            history_video_json = await response.json()
        except Exception as e:
            return f"获取视频回放历史流失败, 错误信息: {str(e)}"
        print(history_video_json)
        if history_video_json["hdr"]["code"] == 200:
            history_video = history_video_json["data"]
            return history_video
        else:
            return status_codes.get(history_video_json["hdr"]["code"], "未知错误")

    @staticmethod
    def hms_to_seconds(time_str: str) -> int:
        """hh:mm:ss / mm:ss 转为相对总秒数"""
        parts = list(map(int, time_str.split(":")))
        if len(parts) == 2:
            m, s = parts
            return m * 60 + s
        elif len(parts) == 3:
            h, m, s = parts
            return h * 3600 + m * 60 + s
        raise ValueError("格式仅支持 mm:ss 或 hh:mm:ss")

    @staticmethod
    def relative_to_unix(base_ts: int, time_str: str) -> int:
        """
        视频相对时间 → Unix秒级时间戳
        :param base_ts: 视频起始基准unix时间戳(秒)
        :param time_str: 视频内时间 如 "02:10" "00:02:10"
        :return: unix时间戳
        """
        offset = DriverMonitorService.hms_to_seconds(time_str)
        return base_ts + offset

    @staticmethod
    async def ctrl_history_video(
        vehicleNo: str,
        channelNo: int,
        ctrlType: Optional[int] = None,
        speed: Optional[int] = None,
        dragTime: Optional[str] = None,
    ):
        """视频回放 控制"""

        session = await get_session()

        url = f"{BASIC_URL}{CTRL_HISTORY_VIDEO}"
        # token放在Authorization头中, 格式为: Bearer token
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]

        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        now_timestamp = time.time()
        payload = {
            "vehicleNo": vehicleNo,
            "channelNo": channelNo,
            "_t": int(now_timestamp * 1000),
        }
        if ctrlType is not None:
            payload["ctrlType"] = ctrlType
        if speed is not None:
            payload["speed"] = speed
        if dragTime is not None:
            # dragTime为年月日时分秒字符串，转换为unix时间戳
            payload["dragTime"] = int(datetime.strptime(dragTime, "%Y-%m-%d %H:%M:%S").timestamp())
        try:
            response = await session.get(url, params=payload, headers=headers)
            ctrl_history_video_json = await response.json()
        except Exception as e:
            return f"视频回放 控制失败, 错误信息: {str(e)}"

        if ctrl_history_video_json["hdr"]["code"] == 200:
            ctrl_history_video = ctrl_history_video_json["data"]
            return ctrl_history_video
        else:
            return status_codes.get(ctrl_history_video_json["hdr"]["code"], "未知错误")

    @staticmethod
    def seconds_to_hms(total_sec: int) -> str:
        h = total_sec // 3600
        m = (total_sec % 3600) // 60
        s = total_sec % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    @staticmethod
    async def get_playback_time(zlmStreamID: str):
        """视频回放 获取播放进度"""
        session = await get_session()
        url = f"{BASIC_URL}{PLAYBACK_TIME}"
        # token放在Authorization头中, 格式为: Bearer token
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {
            "zlmStreamID": zlmStreamID,
            "_t": int(time.time() * 1000),
        }
        try:
            response = await session.get(url, params=payload, headers=headers)
            playback_time_json = await response.json()
        except Exception as e:
            return f"获取视频回放播放进度失败, 错误信息: {str(e)}"
        return playback_time_json["data"]

    @staticmethod
    async def get_download_progress(streamID: str, deviceNo: str):
        """录像下载 获取下载进度"""
        session = await get_session()
        url = f"{BASIC_URL}{DOWNLOAD_PROGRESS}"
        # token放在Authorization头中, 格式为: Bearer token
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {
            "streamID": streamID,
            "deviceNo": deviceNo,
            "_t": int(time.time() * 1000),
        }
        try:
            response = await session.get(url, params=payload, headers=headers)
            download_progress_json = await response.json()
        except Exception as e:
            return f"获取录像下载进度失败, 错误信息: {str(e)}"
        if download_progress_json["hdr"]["code"] == 200:
            download_progress = download_progress_json["data"]
            return download_progress
        else:
            return status_codes.get(download_progress_json["hdr"]["code"], "未知错误")

    @staticmethod
    async def get_file_download(streamID: str, fileName: str):
        """录像下载 录像下载到本地"""
        session = await get_session()
        url = f"{BASIC_URL}{FILE_DOWNLOAD}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "streamID": streamID,
            "fileName": fileName,
            "_t": int(time.time() * 1000),
        }
        try:
            response = await session.get(
                url, params=payload, headers=headers
            )  # MP4 二进制流

            return response
        except Exception as e:
            return f"录像下载到本地失败, 错误信息: {str(e)}"


    @staticmethod
    async def get_download_list():
        """视频回放 获取下载列表"""
        session = await get_session()
        url = f"{BASIC_URL}{DOWNLOAD_STREAMID}"
        # token放在Authorization头中, 格式为: Bearer token
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {
            "_t": int(time.time() * 1000),
        }
        try:
            response = await session.get(url, params=payload, headers=headers)
            download_lists = await response.json()
        except Exception as e:
            return f"获取视频回放下载列表失败, 错误信息: {str(e)}"
        print(download_lists)
        download_list = download_lists["data"]
        if not download_list:
            return []
        return download_list

    # ========== 实时报警记录 ==========

    @staticmethod
    async def create_alarm_record(
        db: AsyncSession, record: schemas.AlarmRecordCreate
    ):
        """创建报警记录"""
        db_record = models.AlarmRecord(**record.model_dump())
        db.add(db_record)
        await db.commit()
        await db.refresh(db_record)
        return db_record



    @staticmethod
    async def query_alarm_data(
        startTime: str,  # 2023-11-01 10:01:01
        endTime: str,  # 2023-11-01 10:01:01
        alarmTypes: list[int],  # 报警类型列表
        handleStatus: int,  # 处理状态
        curPage: int,
        pageNum: int,
        vehicleNo: Optional[str] = None,
        vehicleGuids: Optional[list[int]] = None,
        isAll: Optional[bool] = None,  # 当为true时不再分页
    ):
        """查询报警数据"""

        """获取单台车辆的报警信息"""
        if not vehicleNo and not vehicleGuids:
            return "请输入车牌号或车辆GUID，二选一即可，车辆GUID优先级更高"
        session = await get_session()
        url = f"{BASIC_URL}{ALARM_DATA_URL}"
        # token放在Authorization头中, 格式为: Bearer token
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/json"
        payload = {
            "startTime": startTime,
            "endTime": endTime,
            "alarmTypes": alarmTypes,
            "handleStatus": handleStatus,
            "curPage": curPage,
            "pageNum": pageNum,
        }
        if vehicleNo:
            payload["vehicleNo"] = vehicleNo
        if vehicleGuids:
            payload["vehicleGuids"] = vehicleGuids
        if isAll:
            payload["isAll"] = isAll
        try:
            response = await session.post(url, json=payload, headers=headers)
            alarm_data_json = await response.json()
        except Exception as e:
            return f"获取报警数据失败, 错误信息: {str(e)}"
        if alarm_data_json["hdr"]["code"] == 200:
            alarm_data = alarm_data_json["data"]
            return alarm_data
        else:
            return status_codes.get(alarm_data_json["hdr"]["code"], "未知错误")

    @staticmethod
    async def get_attachment_info(alarmID: str):
        """获取附件信息"""

        session = await get_session()
        url = f"{BASIC_URL}{ATTACHMENT_INFO_URL}"
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        payload = {
            "alarmID": alarmID,
            "_t": int(time.time() * 1000),
        }
        try:
            response = await session.get(url, params=payload, headers=headers)
            attachment_info_json = await response.json()
        except Exception as e:
            return f"获取附件信息失败, 错误信息: {str(e)}"

        data_list = attachment_info_json.get("data") or []
        for item in data_list:
            file_url = item.get("fileUrl", "")
            if file_url and not file_url.startswith("http"):
                item["fileUrl"] = f"https://pro.iotsmart.net{file_url}"
        return data_list

    @staticmethod
    async def get_daily_info(
        dateTime: str,  # 格式2023-09
        vehicleNo: str,
    ):
        """获取某辆车某月每天的日统计信息"""
        session = await get_session()
        url = f"{BASIC_URL}{DAILY_INFO}"
        # token放在Authorization头中, 格式为: Bearer token
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {
            "dateTime": dateTime,
            "vehicleNo": vehicleNo,
        }

        try:
            response = await session.get(url, params=payload, headers=headers)
            alarm_data_json = await response.json()
        except Exception as e:
            return f"获取日统计信息失败, 错误信息: {str(e)}"
        if alarm_data_json["hdr"]["code"] == 200:
            alarm_data = alarm_data_json["data"]
            return alarm_data
        else:
            return status_codes.get(alarm_data_json["hdr"]["code"], "未知错误")


    @staticmethod
    async def get_ws_info():
        """获取websocket的服务器信息"""
        url = f"{BASIC_URL}{GET_WS_INFO}"
        session = await get_session()
        # token放在Authorization头中, 格式为: Bearer token
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        payload = {
            "_t": int(time.time() * 1000),
        }
        response = await session.get(url, params=payload, headers=headers)
        return await response.json()

    # ========== iotsmart 平台拓展接口 ==========

    @staticmethod
    async def get_user_org():
        """获取用户分组信息"""
        session = await get_session()
        url = f"{BASIC_URL}{USER_ORG_URL}"
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        payload = {"_t": int(time.time() * 1000)}
        try:
            response = await session.get(url, params=payload, headers=headers)
            user_org_json = await response.json()
        except Exception as e:
            return f"获取用户分组信息失败, 错误信息: {str(e)}"
        if user_org_json["hdr"]["code"] == 200:
            return user_org_json["data"]
        else:
            return status_codes.get(user_org_json["hdr"]["code"], "未知错误")

    @staticmethod
    async def query_track_page(
        vehicle_no: str,
        start_time: str,
        end_time: str,
        cur_page: int = 1,
        page_num: int = 100,
    ):
        """查询单页轨迹数据"""
        session = await get_session()
        url = f"{BASIC_URL}{TRACK_URL}"
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        params = {
            "startTime": start_time,
            "endTime": end_time,
            "vehicleNo": vehicle_no,
            "curPage": cur_page,
            "pageNum": page_num,
            "_t": int(time.time() * 1000),
        }
        try:
            logger.info(f"[轨迹查询] 请求URL: {url}, params: {params}")
            response = await session.get(url, params=params, headers=headers)
            track_json = await response.json()
            logger.info(f"[轨迹查询] 平台响应: {track_json}")
        except Exception as e:
            return f"查询单页轨迹失败, 错误信息: {str(e)}"
        if track_json["hdr"]["code"] == 200:
            return track_json["data"]
        else:
            return status_codes.get(track_json["hdr"]["code"], "未知错误")

    @staticmethod
    async def query_track_all(
        vehicle_no: str,
        start_time: str,
        end_time: str,
        page_num: int = 100,
    ):
        """分页查询全部轨迹数据，返回完整 dataList 列表"""
        all_points = []
        cur_page = 1
        while True:
            result = await DriverMonitorService.query_track_page(
                vehicle_no, start_time, end_time, cur_page, page_num
            )
            if isinstance(result, str):
                return result
            points = result.get("dataList", [])
            total = result.get("total", 0)
            all_points.extend(points)
            logger.info(
                f"[轨迹查询] page={cur_page}, 本页{len(points)}条, 累计{len(all_points)}/{total}条"
            )
            if len(all_points) >= total or not points:
                break
            cur_page += 1
        all_points.sort(key=lambda p: p.get("time", 0))
        return all_points


    @staticmethod
    async def get_last_vehicle_status():
        """获取用户所有车辆的最后状态（包含最后定位数据）"""
        session = await get_session()
        url = f"{BASIC_URL}{LAST_VEHICLE_STATUS_URL}"
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        params = {"_t": int(time.time() * 1000)}
        try:
            response = await session.get(url, params=params, headers=headers)
            status_json = await response.json()
        except Exception as e:
            return f"获取所有车辆最后状态失败, 错误信息: {str(e)}"
        if status_json["hdr"]["code"] == 200:
            return status_json["data"]
        else:
            return status_codes.get(status_json["hdr"]["code"], "未知错误")

    @staticmethod
    async def get_vehicle_last_position(vehicle_no: str):
        """获取指定车辆的最后位置"""
        result = await DriverMonitorService.get_last_vehicle_status()
        if isinstance(result, str):
            return result
        for item in result:
            last_gps = item.get("lastGpsData", {})
            if last_gps.get("devNo") == vehicle_no or item.get("vehicleNo") == vehicle_no:
                logger.info(f"[最后位置] vehicleNo={vehicle_no}, 位置={last_gps}")
                return last_gps
        logger.warning(f"[最后位置] 未找到 vehicleNo={vehicle_no} 的最后位置")
        return None
    
    @staticmethod
    async def device_reboot(vehicle_nos: list):
        """终端重启（支持批量）"""
        session = await get_session()
        url = f"{BASIC_URL}{RESTART_URL}"
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/json"
        body = {"vehicleNos": vehicle_nos}
        try:
            logger.info(f"[终端重启] 请求URL: {url}, body: {body}")
            response = await session.post(
                url, json=body, headers=headers, timeout=ClientTimeout(total=60)
            )
            result = await response.json()
            logger.info(f"[终端重启] 平台响应: {result}")
        except Exception as e:
            return f"终端重启失败, 错误信息: {str(e)}"
        hdr = result.get("hdr", {})
        failed_list = result.get("data", [])
        if hdr.get("code") == 200:
            if not failed_list:
                logger.info(f"[终端重启] 下发成功，所有车辆重启成功: {vehicle_nos}")
            else:
                logger.warning(f"[终端重启] 下发成功，但部分车辆重启失败: {failed_list}")
        else:
            logger.error(f"[终端重启] 下发失败: {hdr}")
        if result["hdr"]["code"] == 200:
            return result["data"]
        else:
            return status_codes.get(result["hdr"]["code"], "未知错误")

    @staticmethod
    async def restart_vehicle(vehicle_no: str):
        """重启单台车辆（便捷方法）"""
        return await DriverMonitorService.device_reboot([vehicle_no])

    @staticmethod
    async def device_text(
        vehicle_nos: list,
        text: str,
        flag: int = None,
        task_name: str = None,
    ):
        """下发文本到终端（支持批量）"""
        session = await get_session()
        url = f"{BASIC_URL}{TEXT_URL}"
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/json"
        body = {"vehicleNos": vehicle_nos, "text": text}
        if flag is not None:
            body["flag"] = flag
        if task_name is not None:
            body["taskName"] = task_name
        try:
            response = await session.post(
                url, json=body, headers=headers, timeout=ClientTimeout(total=60)
            )
            result = await response.json()
        except Exception as e:
            return f"文本下发失败, 错误信息: {str(e)}"
        hdr = result.get("hdr", {})
        failed_list = result.get("data", [])
        if hdr.get("code") == 200:
            if not failed_list:
                logger.info(f"[文本下发] 下发成功，所有车辆下发成功: {vehicle_nos}, text={text}")
            else:
                logger.warning(f"[文本下发] 下发成功，但部分车辆下发失败: {failed_list}")
        else:
            logger.error(f"[文本下发] 下发失败: {hdr}")
        if result["hdr"]["code"] == 200:
            return result["data"]
        else:
            return status_codes.get(result["hdr"]["code"], "未知错误")

    @staticmethod
    async def send_trans_msg(
        vehicle_nos: list,
        trans_type: int,
        trans_data: str,
        task_name: str = None,
    ):
        """JT808 自定义透传指令下发"""
        session = await get_session()
        url = f"{BASIC_URL}{TRANS_MSG_URL}"
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/json"
        body = {
            "transType": trans_type,
            "transData": trans_data,
            "vehicleNos": vehicle_nos,
        }
        if task_name is not None:
            body["taskName"] = task_name
        try:
            response = await session.post(
                url, json=body, headers=headers, timeout=ClientTimeout(total=60)
            )
            result = await response.json()
        except Exception as e:
            return f"透传指令下发失败, 错误信息: {str(e)}"
        hdr = result.get("hdr", {})
        if hdr.get("code") == 200:
            failed_list = result.get("data", [])
            if not failed_list:
                logger.info(f"[透传下发] 下发成功，所有车辆下发成功: {vehicle_nos}, transType={trans_type}")
            else:
                logger.warning(f"[透传下发] 下发成功，但部分车辆下发失败: {failed_list}")
        else:
            logger.error(f"[透传下发] 下发失败: {hdr}")
        if result["hdr"]["code"] == 200:
            return result["data"]
        else:
            return status_codes.get(result["hdr"]["code"], "未知错误")

    @staticmethod
    async def get_dev_param(vehicle_no: str, param_ids: str = None):
        """查询终端参数"""
        session = await get_session()
        url = f"{BASIC_URL}{GET_DEV_PARAM_URL}"
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        params = {"vehicleNo": vehicle_no, "_t": int(time.time() * 1000)}
        if param_ids is not None:
            params["paramIDs"] = param_ids
        try:
            response = await session.get(url, params=params, headers=headers)
            result = await response.json()
        except Exception as e:
            return f"查询终端参数失败, 错误信息: {str(e)}"
        if result["hdr"]["code"] == 200:
            return result["data"]
        else:
            return status_codes.get(result["hdr"]["code"], "未知错误")

    @staticmethod
    async def set_dev_param(vehicle_nos: list, items: list):
        """设置终端参数"""
        session = await get_session()
        url = f"{BASIC_URL}{SET_DEV_PARAM_URL}"
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/json"
        body = {
            "vehicleNos": vehicle_nos,
            "items": items,
            "_t": int(time.time() * 1000),
        }
        try:
            response = await session.post(
                url, json=body, headers=headers, timeout=ClientTimeout(total=60)
            )
            result = await response.json()
        except Exception as e:
            return f"设置终端参数失败, 错误信息: {str(e)}"
        hdr = result.get("hdr", {})
        if hdr.get("code") == 200:
            failed_list = result.get("data", [])
            if not failed_list:
                logger.info(f"[设置终端参数] 设置成功，所有车辆设置成功: {vehicle_nos}")
            else:
                logger.warning(f"[设置终端参数] 设置成功，但部分车辆设置失败: {failed_list}")
        else:
            logger.error(f"[设置终端参数] 设置失败: {hdr}")
        if result["hdr"]["code"] == 200:
            return result["data"]
        else:
            return status_codes.get(result["hdr"]["code"], "未知错误")


    @staticmethod
    def get_location_data():
        """读取定位数据（从 MinIO 按 devNo 分文件读取，合并为 {devNo: [points...]} 格式）"""
        result = {}
        try:
            objects = minioserve.list_objects(prefix=LOCATION_MINIO_PREFIX + "/")
        except Exception as e:
            logger.warning(f"[MinIO列出定位文件失败] {e}")
            return {}
        for obj in objects:
            # object_name 形如 test/driver_monitor/location/527086498786.json
            name = obj.object_name.rsplit("/", 1)[-1]
            if not name.endswith(".json"):
                continue
            dev_no = name[:-5]
            try:
                raw = minioserve.download_file(obj.object_name)
                points = json.loads(raw.decode("utf-8"))
                if isinstance(points, list):
                    result[dev_no] = points
            except Exception as e:
                logger.warning(f"[MinIO读取定位文件失败] devNo={dev_no} err={e}")
        return result

    @staticmethod
    async def get_dev_onoffline_data(vehicleNo: str, startTime: str, endTime: str, curPage: int = 1, pageNum: int = 20, isAll: bool = None):
        """车辆上下线查询"""
        session = await get_session()
        url = f"{BASIC_URL}{QUERY_ONOFFLINE_DATA}"
        token = await DriverMonitorService.login()
        if isinstance(token, tuple):
            return token[1]
        headers = DriverMonitorService.build_headers(token)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {
            "vehicleNo": vehicleNo,
            "startTime": startTime,
            "endTime": endTime,
            "curPage": curPage,
            "pageNum": pageNum,
            "_t": int(time.time() * 1000),
        }
        if isAll:
            payload["isAll"] = isAll
        try:
            response = await session.get(url, params=payload, headers=headers)
            onoffline_data_json = await response.json()
        except Exception as e:
            return f"获取上下线记录失败, 错误信息: {str(e)}"
        if onoffline_data_json["hdr"]["code"] == 200:
            onoffline_data = onoffline_data_json["data"]
            return onoffline_data
        else:
            return status_codes.get(onoffline_data_json["hdr"]["code"], "未知错误")

    @staticmethod
    async def get_latest_onoffline_time(vehicleNo: str):
        """获取车辆最新上下线时间（取最近一次上线 + 最近一次下线）"""
        today_date = date.today()
        end_time = today_date.strftime("%Y-%m-%d 23:59:59")
        start_time = (today_date - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
        data = await DriverMonitorService.get_dev_onoffline_data(
            vehicleNo=vehicleNo,
            startTime=start_time,
            endTime=end_time,
            curPage=1,
            pageNum=10,
        )
        if isinstance(data, str):
            ws_logger.warning(f"[上下线查询] 平台返回错误: {data}")
            return data
        records = data.get("dataList") if isinstance(data, dict) else []
        if not records:
            return {"vehicleNo": vehicleNo, "latest_online_time": None, "latest_offline_time": None}
        # dataList 默认按 eventTime 倒序返回，分别取最近一条上线/下线事件
        latest_online = next((r for r in records if r.get("isOnline") is True), None)
        latest_offline = next((r for r in records if "isOnline" not in r or r.get("isOnline") is False), None)
        # datetime.fromtimestamp(dead_time).strftime("%Y-%m-%d %H:%M:%S")
        if latest_online is not None:
            latest_online1 = latest_online.get("eventTime")
            latest_online_time = datetime.fromtimestamp(latest_online1).strftime("%Y-%m-%d %H:%M:%S")
        else:
            latest_online_time = None
        if latest_offline is not None:
            latest_offline1 = latest_offline.get("eventTime")
            latest_offline_time = datetime.fromtimestamp(latest_offline1).strftime("%Y-%m-%d %H:%M:%S")
        else:
            latest_offline_time = None
        return {
            "vehicleNo": vehicleNo,
            "latest_online_time": latest_online_time,
            "latest_offline_time": latest_offline_time,
        }

    @staticmethod
    def get_online_vehicle_snapshot() -> list:
        """返回当前在线车辆缓存快照（供 SSE 首次连接时推送初始数据）

        online_vehicle_cache 按 guid/no/dev 三套 key 存同一辆车，这里以 guid 为准去重。
        """
        seen = set()
        snapshot = []
        for key, veh in online_vehicle_cache.items():
            if not key.startswith("guid:"):
                continue
            guid = veh.get("vehicleGuid")
            if guid in seen:
                continue
            seen.add(guid)
            snapshot.append(veh)
        return snapshot

    @staticmethod
    async def ensure_iotsmart_ws_connected() -> bool | dict:
        """
        检查 iotsmart 平台 WebSocket 是否已连接并完成初始在线列表同步。
        **只检查状态，不启动 WS**（统一通过 /ws_start 接口启动 WebSocketService）。
        :return: True=已就绪；dict=错误信息（未启动/内网不可用等）
        """
        if WebSocketService.is_running() and _online_list_initialized:
            return True
        if not WebSocketService.is_running():
            return {"_status": "not_started", "isOnline": False, "message": "WebSocket 未启动，请先调用 /ws_start 接口"}
        # 已运行但尚未收到初始列表
        return {"_status": "initializing", "isOnline": False, "message": "WebSocket 正在连接，初始在线列表尚未同步，请稍后重试"}



def _cache_online_vehicle(veh: dict):
    """把一辆在线车辆写入缓存（按guid/车牌/终端号三套key索引）"""
    guid = veh.get("vehicleGuid")
    veh_no = veh.get("vehicleNo")
    dev_no = veh.get("devNo")
    entry = dict(veh)
    entry["isOnline"] = True
    entry["updateTime"] = int(time.time())
    if guid is not None:
        online_vehicle_cache[f"guid:{guid}"] = entry
    if veh_no:
        online_vehicle_cache[f"no:{veh_no}"] = entry
    if dev_no:
        online_vehicle_cache[f"dev:{dev_no}"] = entry

# ========== WebScket 长连接 ==========
# 地址缓存：(lng_001, lat_001) -> address，量化到 0.001°(约100m)，避免高频请求
_address_cache: dict = {}


async def reverse_geocode(lng: float, lat: float) -> str:
    """经纬度转地址（高德逆地理编码），带缓存"""
    key = (round(lng, 3), round(lat, 3))
    if key in _address_cache:
        return _address_cache[key]
    if not settings.AMAP_KEY:
        return ""
    try:
        session = await get_session()
        url = "https://restapi.amap.com/v3/geocode/regeo"
        params = {"location": f"{lng},{lat}", "key": settings.AMAP_KEY, "extensions": "base"}
        resp = await session.get(url, params=params)
        data = await resp.json()
        if data.get("status") == "1":
            addr = data["regeocode"]["formatted_address"]
            _address_cache[key] = addr
            return addr
    except Exception as e:
        ws_logger.warning(f"逆地理编码失败: {e}")
    return ""


async def save_location_to_file(data: dict) -> None:
    """缓存30秒内所有点位，30秒到了：SSE只推最新1个点 + 写入MinIO（按devNo分文件）"""
    global last_location_write_time, latest_points
    # 1. 每次收到都加入缓存列表
    location_list = data.get("data", [])
    if location_list:
        latest_points.extend(location_list)

    # 2. 不到30秒只缓存，不推送不写文件
    now = time.time()
    if now - last_location_write_time < LOCATION_INTERVAL:
        return
    # 3. 30秒到了
    if not latest_points:
        return
    last_location_write_time = now
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # SSE只推最新的一个点给前端，并附加逆地理编码地址
    latest_point = dict(latest_points[-1])
    lng = latest_point.get("longitude", 0) / 1e6
    lat = latest_point.get("latitude", 0) / 1e6
    latest_point["address"] = await reverse_geocode(lng, lat)
    await sse_mgr.broadcast(
        {"saveTime": now_str, "data": latest_point},
        event="location",
    )
    # 按 devNo 分组（只存每个 devNo 的最新一个点，和推送给前端的数据一致）
    grouped: dict = {}
    for point in latest_points:
        dev_no = point.get("devNo", "unknown")
        grouped[dev_no] = point  # 直接覆盖，保留最后一个

    # 写入 MinIO：每个 devNo 一个文件，路径 test/driver_monitor/location/{devNo}.json
    # 采用「下载-追加-上传」模式；下载失败视为新建
    for dev_no, point in grouped.items():
        object_name = f"{LOCATION_MINIO_PREFIX}/{dev_no}.json"
        existing_points = []
        try:
            raw = await asyncio.to_thread(minioserve.download_file, object_name)
            existing_points = json.loads(raw.decode("utf-8"))
            if not isinstance(existing_points, list):
                existing_points = []
        except Exception:
            # 文件不存在或解析失败，按新建处理
            existing_points = []
        existing_points.append(point)  # 只追加最新一个点
        payload = json.dumps(existing_points, ensure_ascii=False).encode("utf-8")
        try:
            await asyncio.to_thread(
                minioserve.upload_file,
                payload,
                object_name,
                None,
                "application/json",
            )
        except Exception as e:
            ws_logger.warning(f"[MinIO写入定位数据失败] devNo={dev_no} err={e}")

    # 清空缓存，开始下一轮30秒
    latest_points = []


class WebSocketService:
    """WebSocket 长连接管理（启停控制 + 自动重连）"""

    task: asyncio.Task | None = None
    stop_flag: asyncio.Event | None = None

    @classmethod
    def is_running(cls) -> bool:
        return cls.task is not None and not cls.task.done()

    @classmethod
    async def start(cls) -> str:
        if cls.is_running():
            return "已运行中"
        cls.stop_flag = asyncio.Event()
        cls.task = asyncio.create_task(cls.run(cls.stop_flag))
        return "启动成功"

    @classmethod
    async def stop(cls) -> str:
        if not cls.is_running():
            return "未运行"
        if cls.stop_flag:
            cls.stop_flag.set()
        if cls.task:
            cls.task.cancel()
            try:
                await cls.task
            except asyncio.CancelledError:
                pass
            cls.task = None
        return "已停止"

    @staticmethod
    async def ws_heartbeat(ws, stop_event: asyncio.Event) -> None:
        """定时发送心跳消息"""
        req_sn = 1
        while not stop_event.is_set():
            heartbeat_msg = {
                "hdr": {
                    "message": "",
                    "msgType": MSG_TYPE_HEARTBEAT_REQ,
                    "reqSN": req_sn,
                    "respSN": 0,
                }
            }
            await ws.send_json(heartbeat_msg)
            ws_logger.info(f"[心跳发送] reqSN={req_sn}")
            req_sn += 1
            await asyncio.sleep(HEARTBEAT_INTERVAL)

    @staticmethod
    async def ws_receive(ws, stop_event: asyncio.Event) -> None:
        """接收服务器消息并按 msgType 分类处理，维护在线状态缓存并转发给前端 SSE"""
        global online_vehicle_cache, _online_list_initialized
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    msg_type = data.get("hdr", {}).get("msgType")
                    if msg_type == MSG_TYPE_VEHICLE_ONLINE_LIST_FIRST:
                        ws_logger.info(f"[车辆在线列表-首推] {data}")
                    elif msg_type == MSG_TYPE_HEARTBEAT_RESP:
                        ws_logger.info(f"[心跳响应] {data}")
                    elif msg_type == MSG_TYPE_VEHICLE_ONLINE_LIST:
                        # 8000: 初始在线列表（登录后首推或重连后重推），全量重建缓存
                        ws_logger.info(f"[车辆在线列表] {data}")
                        online_list = data.get("onlineVehicleInfo", [])
                        if not online_list and "data" in data:
                            online_list = data["data"].get("onlineVehicleInfo", [])
                        online_vehicle_cache.clear()
                        for veh in online_list:
                            _cache_online_vehicle(veh)
                        _online_list_initialized = True
                        ws_logger.info(f"[初始化完成] 当前在线车辆数: {len(online_list)}")
                        await sse_mgr.broadcast(
                            {"data": online_list},
                            event="vehicle_online_list",
                        )
                    elif msg_type == MSG_TYPE_VEHICLE_ON_OFF:
                        # 8001: 车辆上下线，更新缓存并广播
                        ws_logger.info(f"[车辆上下线] {data}")
                        veh_data = data.get("data", {})
                        is_online = veh_data.get("isOnline", False)
                        guid = veh_data.get("vehicleGuid")
                        veh_no = veh_data.get("vehicleNo")
                        dev_no = veh_data.get("devNo")
                        if is_online:
                            _cache_online_vehicle(veh_data)
                        else:
                            # 下线：删除三套 key
                            for k in (f"guid:{guid}", f"no:{veh_no}", f"dev:{dev_no}"):
                                online_vehicle_cache.pop(k, None)
                        await sse_mgr.broadcast(
                            {"data": veh_data},
                            event="vehicle_status",
                        )
                    elif msg_type == MSG_TYPE_LOCATION:
                        ws_logger.info(f"[定位数据] {data}")
                        await save_location_to_file(data)

                    elif msg_type == MSG_TYPE_ALARM:
                        ws_logger.info(f"[报警数据] {data}")
                        body = {k: v for k, v in data.items() if k != "hdr"}
                        await sse_mgr.broadcast(body, event="alarm")
                        # 异步入库（不阻塞 SSE 推送）
                        ws_logger.info(f"[报警推送] 创建入库任务: alarmType={body.get('data', [{}])[0].get('alarmType') if body.get('data') else 'N/A'}")
                        asyncio.create_task(DriverMonitorService._save_alarm_to_db(body))
                    elif msg_type in (MSG_TYPE_ATTACHMENT, MSG_TYPE_ATTACHMENT_8005):
                        ws_logger.info(f"[附件信息] {data}")
                    else:
                        ws_logger.info(f"[未知消息类型 {msg_type}] {data}")
                elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.CLOSING):
                    ws_logger.info(f"[WebSocket] 连接关闭 type={msg.type}")
                    break
                elif msg.type == WSMsgType.BINARY:
                    try:
                        binary_data = json.loads(msg.data.decode())
                        ws_logger.info(f"[二进制数据] {binary_data}")
                    except json.JSONDecodeError:
                        ws_logger.info("[二进制数据] 非JSON格式")
                elif msg.type == WSMsgType.ERROR:
                    ws_logger.info(f"[WebSocket] 错误: {msg.data}")
                    break
        except Exception as e:
            ws_logger.info(f"[接收异常] {e}")

    @classmethod
    async def run(cls, stop_flag: asyncio.Event) -> None:
        global _online_list_initialized, online_vehicle_cache
        ws_session = ClientSession(
            connector=TCPConnector(limit=5, ssl=False),
            timeout=ClientTimeout(total=None),
        )

        ws_logger.info("[WebSocket] 任务启动，开始连接平台")

        try:
            while not stop_flag.is_set():
                try:
                    # 给登录加超时
                    try:
                        token = await asyncio.wait_for(DriverMonitorService.login(), timeout=8)
                    except asyncio.TimeoutError:
                        ws_logger.error("[登录超时] 8秒未响应")
                        await asyncio.sleep(1)
                        continue

                    if isinstance(token, tuple):
                        ws_logger.error(f"[登录失败] {token[1]}")
                        await asyncio.sleep(2)
                        continue
                    ws_logger.info(f"[登录成功] token={token[:20]}...")

                    # 动态获取 ws_url
                    try:
                        ws_info = await asyncio.wait_for(
                            DriverMonitorService.get_ws_info(), timeout=5
                        )
                        if isinstance(ws_info, dict):
                            ws_data = ws_info.get("data", {})
                            ws_addr = ws_data.get("websocketAddr") or "pro.iotsmart.net"
                            ws_port = ws_data.get("websocketPort") or 7204
                            ws_url = f"ws://{ws_addr}:{ws_port}"
                        else:
                            ws_url = WS_URL
                    except Exception as e:
                        ws_logger.warning(f"[动态获取ws_url失败] {e}，使用配置常量 {WS_URL}")
                        ws_url = WS_URL

                    url = f"{ws_url}{WS_LOGIN_URL}"
                    try:
                        ws_conn = await asyncio.wait_for(
                            ws_session.ws_connect(url, params={"token": token}),
                            timeout=10,
                        )
                    except Exception as e:
                        ws_logger.warning(f"[WS连接失败/超时] {e}")
                        await asyncio.sleep(2)
                        continue

                    async with ws_conn as ws:
                        # 等首条8000消息
                        try:
                            login_msg = await asyncio.wait_for(ws.receive(), timeout=10)
                        except asyncio.TimeoutError:
                            ws_logger.warning("[WS] 10秒未收到8000消息")
                            login_msg = None

                        if login_msg and login_msg.type == WSMsgType.TEXT:
                            try:
                                first_data = json.loads(login_msg.data)
                                first_msg_type = first_data.get("hdr", {}).get("msgType")
                                ws_logger.info(f"[登录响应] {first_data}")
                                if first_msg_type == MSG_TYPE_VEHICLE_ONLINE_LIST:
                                    online_list = first_data.get("onlineVehicleInfo", [])
                                    if not online_list and "data" in first_data:
                                        online_list = first_data["data"].get("onlineVehicleInfo", [])
                                    online_vehicle_cache.clear()
                                    for veh in online_list:
                                        _cache_online_vehicle(veh)
                                    _online_list_initialized = True
                                    ws_logger.info(f"[初始化完成] 当前在线车辆数: {len(online_list)}")
                                    await sse_mgr.broadcast(
                                        {"data": online_list},
                                        event="vehicle_online_list",
                                    )
                            except json.JSONDecodeError:
                                ws_logger.info(f"[WebSocket第一条消息] JSON解析失败: {str(login_msg.data)[:500]}")

                        heartbeat_task = asyncio.create_task(cls.ws_heartbeat(ws, stop_flag))
                        receive_task = asyncio.create_task(cls.ws_receive(ws, stop_flag))
                        done, pending = await asyncio.wait(
                            [heartbeat_task, receive_task],
                            return_when=asyncio.FIRST_COMPLETED,
                        )
                        for t in pending:
                            t.cancel()
                        if pending:
                            await asyncio.gather(*pending, return_exceptions=True)
                except asyncio.CancelledError:
                    ws_logger.info("[任务取消]")
                    break
                except Exception as e:
                    ws_logger.info(f"[连接异常] {e}，2秒后重连")
                    await asyncio.sleep(2)
        finally:
            if ws_session and not ws_session.closed:
                await ws_session.close()
                ws_logger.info("[WebSocket Session已关闭]")

