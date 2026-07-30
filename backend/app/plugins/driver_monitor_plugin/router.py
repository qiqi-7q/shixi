from datetime import date, datetime
from typing import Optional
from app.core.database import AsyncSession, get_db
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.plugins.driver_monitor_plugin import schemas, services

router = APIRouter()

# ===================================平台接口=============================


@router.get("/info")
async def get_monitor_info(
    db: AsyncSession = Depends(get_db),
    vin_code: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    page: int = Query(1, ge=1, description="页码"),  # >=1
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """获取监控信息"""
    monitorinfo = await services.DriverMonitorService.get_monitor_info(
        db, vin_code, start_time, end_time, page, page_size, sort_by, sort_order
    )
    if isinstance(monitorinfo, str):
        return {"message": monitorinfo, "code": 400, "data": None}
    return {"message": "获取监控信息成功", "data": monitorinfo, "code": 200}


# ===================================第三方平台接口=============================


@router.get("/car_info")
async def get_car_info():
    """获取用户车辆基础信息"""
    carinfo = await services.DriverMonitorService.get_car_info()
    if isinstance(carinfo, str):
        return {"message": carinfo, "code": 400, "data": None}
    return {"message": "获取用户车辆基础信息成功", "data": carinfo, "code": 200}


@router.get("/realtime_audio")
async def get_realtime_audio(vehicleNo: str, channelNo: int):
    """实时视频"""
    realtime_audio = await services.DriverMonitorService.get_realtime_audio(
        vehicleNo, channelNo
    )
    if isinstance(realtime_audio, str):
        return {"message": realtime_audio, "code": 400, "data": None}
    return {"message": "获取实时视频成功", "data": realtime_audio, "code": 200}


@router.get("/realtime_monitor")
async def get_realtime_monitor(vehicleNo: str, channelNo: int):
    """实时音频监听"""
    realtime_monitor = await services.DriverMonitorService.get_realtime_monitor(
        vehicleNo, channelNo
    )
    if isinstance(realtime_monitor, str):
        return {"message": realtime_monitor, "code": 400, "data": None}
    return {"message": "获取实时音频监听成功", "data": realtime_monitor, "code": 200}


@router.get("/realtime_talk")
async def get_realtime_talk(vehicleNo: str, channelNo: int, playerProtocol: int = 2):
    """实时对讲"""
    realtime_talk = await services.DriverMonitorService.get_realtime_talk(
        vehicleNo, channelNo, playerProtocol
    )
    if isinstance(realtime_talk, str):
        return {"message": realtime_talk, "code": 400, "data": None}
    return {"message": "获取实时对讲成功", "data": realtime_talk, "code": 200}


@router.get("/media_list")
async def get_media_list(
    vehicleNo: str,
    startTime: str,
    endTime: str,
    channelNo: Optional[int] = None,
    alarmFlag: Optional[int] = None,
    mediaType: Optional[int] = None,
    bitStreamType: Optional[int] = None,
    storageType: Optional[int] = None,
):
    """视频回放 获取媒体列表"""
    media_list = await services.DriverMonitorService.get_media_list(
        vehicleNo,
        startTime,
        endTime,
        channelNo,
        alarmFlag,
        mediaType,
        bitStreamType,
        storageType,
    )
    if isinstance(media_list, str):
        return {"message": media_list, "code": 400, "data": None}
    return {"message": "获取视频回放媒体列表成功", "data": media_list, "code": 200}


@router.get("/history_video")
async def get_history_video(
    vehicleNo: str,
    channelNo: int,
    startTime: str,
    endTime: str,
    playType: Optional[int] = None,
    mediaType: Optional[int] = None,
    speed: Optional[int] = None,
    storageType: Optional[int] = None,
    isDownload: Optional[bool] = None,
    isSubCode: Optional[bool] = None,
):
    """视频回放 请求历史流"""
    history_video = await services.DriverMonitorService.get_history_video(
        vehicleNo=vehicleNo,
        channelNo=channelNo,
        startTime=startTime,
        endTime=endTime,
        playType=playType,
        mediaType=mediaType,
        speed=speed,
        storageType=storageType,
        isDownload=isDownload,
        isSubCode=isSubCode,
    )
    if isinstance(history_video, str):
        return {"message": history_video, "code": 400, "data": None}
    return {"message": "获取视频回放历史流成功", "data": history_video, "code": 200}


@router.get("/ctrl_history_video")
async def ctrl_history_video(
    vehicleNo: str,
    channelNo: int,
    ctrlType: Optional[int] = None,
    speed: Optional[int] = None,
    dragTime: Optional[str] = None,
):
    """视频回放 控制"""
    ctrl_history_videos = await services.DriverMonitorService.ctrl_history_video(
        vehicleNo,
        channelNo,
        ctrlType,
        speed,
        dragTime,
    )
    if isinstance(ctrl_history_videos, str):
        return {"message": ctrl_history_videos, "code": 400, "data": None}
    return {"message": "视频回放 控制成功", "data": ctrl_history_videos, "code": 200}


@router.get("/playback_time")
async def get_playback_time(zlmStreamID: str):
    """视频回放 获取播放进度"""
    playback_time = await services.DriverMonitorService.get_playback_time(zlmStreamID)
    return {"message": "获取视频回放播放进度成功", "data": playback_time, "code": 200}


@router.get("/download_list")
async def get_download_list():
    """视频回放 获取下载列表"""
    download_list = await services.DriverMonitorService.get_download_list()
    if isinstance(download_list, str):
        return {"message": download_list, "code": 400, "data": None}
    return {"message": "获取视频回放下载列表成功", "data": download_list, "code": 200}

@router.get("/download_progress")
async def get_download_progress(streamID: str, deviceNo: str):
    """录像下载 获取下载进度"""
    download_progress = await services.DriverMonitorService.get_download_progress(
        streamID, deviceNo
    )
    if isinstance(download_progress, str):
        return {"message": download_progress, "code": 400, "data": None}
    return {"message": "获取录像下载进度成功", "data": download_progress, "code": 200}


@router.get("/file_download")
async def get_file_download(streamID: str, fileName: str):
    """录像下载 录像下载到本地"""
    file_download = await services.DriverMonitorService.get_file_download(
        streamID, fileName
    )
    if isinstance(file_download, str):
        return {"message": file_download, "code": 400, "data": None}

    async def stream_file():
        try:
            async for chunk in file_download.content.iter_chunked(64 * 1024):
                yield chunk
        finally:
            file_download.release()

    content_type = file_download.headers.get("Content-Type", "video/mp4")
    return StreamingResponse(
        stream_file(),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{fileName}"'},
    )


@router.get("/ws_info")
async def get_ws_info():
    """获取websocket的服务器信息"""
    ws_info = await services.DriverMonitorService.get_ws_info()
    if isinstance(ws_info, str):
        return {"message": ws_info, "code": 400, "data": None}
    return {"message": "获取websocket的服务器信息成功", "data": ws_info, "code": 200}
# ========== iotsmart 平台拓展接口 ==========


@router.get("/user_org")
async def get_user_org():
    """获取用户分组信息"""
    user_org = await services.DriverMonitorService.get_user_org()
    if isinstance(user_org, str):
        return {"message": user_org, "code": 400, "data": None}
    return {"message": "获取用户分组信息成功", "data": user_org, "code": 200}


@router.get("/track_page")
async def get_track_page(
    vehicleNo: str,
    startTime: str,
    endTime: str,
    curPage: int = 1,
    pageNum: int = 100,
):
    """查询单页轨迹数据"""
    track_page = await services.DriverMonitorService.query_track_page(
        vehicleNo, startTime, endTime, curPage, pageNum
    )
    if isinstance(track_page, str):
        return {"message": track_page, "code": 400, "data": None}
    return {"message": "查询单页轨迹成功", "data": track_page, "code": 200}


@router.get("/track_all")
async def get_track_all(
    vehicleNo: str,
    startTime: str,
    endTime: str,
    pageNum: int = 100,
):
    """查询全部轨迹数据"""
    track_all = await services.DriverMonitorService.query_track_all(
        vehicleNo, startTime, endTime, pageNum
    )
    if isinstance(track_all, str):
        return {"message": track_all, "code": 400, "data": None}
    return {
        "message": "查询全部轨迹成功",
        "data": track_all,
        "total": len(track_all),
        "code": 200,
    }

@router.get("/last_vehicle_status")
async def get_last_vehicle_status():
    """获取所有车辆最后状态"""
    last_status = await services.DriverMonitorService.get_last_vehicle_status()
    if isinstance(last_status, str):
        return {"message": last_status, "code": 400, "data": None}
    return {"message": "获取所有车辆最后状态成功", "data": last_status, "code": 200}


@router.get("/vehicle_last_position")
async def get_vehicle_last_position(vehicleNo: str):
    """获取指定车辆最后位置"""
    last_position = await services.DriverMonitorService.get_vehicle_last_position(
        vehicleNo
    )
    if isinstance(last_position, str):
        return {"message": last_position, "code": 400, "data": None}
    return {"message": "获取指定车辆最后位置成功", "data": last_position, "code": 200}


@router.get("/device_reboot")
async def device_reboot(vehicleNos: str):
    """终端重启（批量，多个车牌用逗号分隔）"""
    vehicle_nos = [v.strip() for v in vehicleNos.split(",") if v.strip()]
    result = await services.DriverMonitorService.device_reboot(vehicle_nos)
    if isinstance(result, str):
        return {"message": result, "code": 400, "data": None}
    return {"message": "终端重启下发成功", "data": result, "code": 200}


@router.get("/restart_vehicle")
async def restart_vehicle(vehicleNo: str):
    """重启单台车辆"""
    result = await services.DriverMonitorService.restart_vehicle(vehicleNo)
    if isinstance(result, str):
        return {"message": result, "code": 400, "data": None}
    return {"message": "车辆重启下发成功", "data": result, "code": 200}


@router.get("/device_text")
async def device_text(
    vehicleNos: str,
    text: str,
    flag: Optional[int] = None,
    taskName: Optional[str] = None,
):
    """下发文本到终端（批量，多个车牌用逗号分隔）"""
    vehicle_nos = [v.strip() for v in vehicleNos.split(",") if v.strip()]
    result = await services.DriverMonitorService.device_text(
        vehicle_nos, text, flag, taskName
    )
    if isinstance(result, str):
        return {"message": result, "code": 400, "data": None}
    return {"message": "文本下发成功", "data": result, "code": 200}


@router.get("/trans_msg")
async def send_trans_msg(
    vehicleNos: str,
    transType: int,
    transData: str,
    taskName: Optional[str] = None,
):
    """JT808 透传指令下发（批量，多个车牌用逗号分隔）"""
    vehicle_nos = [v.strip() for v in vehicleNos.split(",") if v.strip()]
    result = await services.DriverMonitorService.send_trans_msg(
        vehicle_nos, transType, transData, taskName
    )
    if isinstance(result, str):
        return {"message": result, "code": 400, "data": None}
    return {"message": "透传指令下发成功", "data": result, "code": 200}


@router.get("/dev_param")
async def get_dev_param(
    vehicleNo: str,
    paramIDs: Optional[str] = None,
):
    """查询终端参数"""
    result = await services.DriverMonitorService.get_dev_param(vehicleNo, paramIDs)
    if isinstance(result, str):
        return {"message": result, "code": 400, "data": None}
    return {"message": "查询终端参数成功", "data": result, "code": 200}


@router.get("/set_dev_param")
async def set_dev_param(
    vehicleNos: str,
    items: str,
):
    """设置终端参数（批量，vehicleNos 多个车牌用逗号分隔；items 为 JSON 字符串）"""
    import json as _json

    vehicle_nos = [v.strip() for v in vehicleNos.split(",") if v.strip()]
    try:
        items_list = _json.loads(items)
    except _json.JSONDecodeError:
        return {"message": "items 参数不是有效的 JSON", "code": 400, "data": None}
    result = await services.DriverMonitorService.set_dev_param(vehicle_nos, items_list)
    if isinstance(result, str):
        return {"message": result, "code": 400, "data": None}
    return {"message": "设置终端参数成功", "data": result, "code": 200}


@router.get("/ws_status")
async def ws_status():
    """查询 WebSocket 状态"""
    return {
        "message": "success",
        "data": {"running": services.WebSocketService.is_running()},
        "code": 200,
    }


@router.get("/location_data")
async def get_location_data(devNo: Optional[str] = None):
    """获取定位数据（按devNo分组，只返回当天数据）
    - devNo: 设备号，不传则返回所有设备号列表；传了则返回该设备当天的全部点位
    """
    all_data = services.DriverMonitorService.get_location_data()
    if not all_data:
        return {"message": "暂无定位数据", "code": 200, "data": {"items": []}}
    if not devNo:
        return {"message": "获取设备列表成功", "code": 200, "data": {"devNos": list(all_data.keys())}}
    # 只返回当天数据（time 字段为 Unix 时间戳，秒）
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    points = [p for p in all_data.get(devNo, []) if p.get("time", 0) >= today_start]
    if not points:
        return {"message": f"设备 {devNo} 今天无定位数据", "code": 200, "data": {"items": []}}
    return {
        "message": "获取定位数据成功",
        "code": 200,
        "data": {"items": points, "total": len(points)},
    }

# ========== 实时报警记录接口 ==========

@router.post("/alarm_record")
async def create_alarm_record(
    record: schemas.AlarmRecordCreate, db: AsyncSession = Depends(get_db)
):
    """创建报警记录"""
    result = await services.DriverMonitorService.create_alarm_record(db, record)
    return {"message": "报警记录创建成功", "code": 200, "data": schemas.AlarmRecordResponse.model_validate(result).model_dump()}

@router.get("/alarm_records")
async def get_alarm_records(
    db: AsyncSession = Depends(get_db),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    alarm_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
):
    """分页查询报警记录"""
    result = await services.DriverMonitorService.get_alarm_records(
        db,
        start_time=start_time,
        end_time=end_time,
        alarm_type=alarm_type,
        page=page,
        page_size=page_size,
    )

    return {
        "message": "查询成功",
        "code": 200,
        "data": {
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
            "records": result["records"],
        },
    }


@router.get("/alarm_type_stats")
async def get_alarm_type_stats(
    db: AsyncSession = Depends(get_db),
    vin_code: str = Query(..., description="车辆VIN号"),
    target_date: Optional[date] = None,
):
    """统计指定车辆某天各报警类型的次数（默认当天）"""
    result = await services.DriverMonitorService.get_alarm_type_stats(
        db, vin_code=vin_code, target_date=target_date
    )
    return {"message": "查询成功", "code": 200, "data": result}


@router.post("/query_alarm_data")
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
    """获取单台车辆的报警信息"""
    alarm_data = await services.DriverMonitorService.query_alarm_data(
        startTime=startTime,
        endTime=endTime,
        alarmTypes=alarmTypes,
        handleStatus=handleStatus,
        curPage=curPage,
        pageNum=pageNum,
        vehicleNo=vehicleNo,
        vehicleGuids=vehicleGuids,
        isAll=isAll,
    )
    if isinstance(alarm_data, str):
        return {"message": alarm_data, "code": 400, "data": None}
    return {"message": "获取单台车辆的报警信息成功", "data": alarm_data, "code": 200}


@router.get("/get_attachment_info")
async def get_attachment_info(alarmID: str):
    """获取附件信息"""
    attachment_info = await services.DriverMonitorService.get_attachment_info(alarmID)
    if isinstance(attachment_info, str):
        return {"message": attachment_info, "code": 400, "data": None}
    return {"message": "获取附件信息成功", "data": attachment_info, "code": 200}

@router.get("/daily_info")
async def get_daily_info(
    dateTime: str,  # 格式2023-09
    vehicleNo: str,
):
    """获取某辆车某月每天的日统计信息"""
    daily_info = await services.DriverMonitorService.get_daily_info(
        dateTime=dateTime,
        vehicleNo=vehicleNo,
    )
    if isinstance(daily_info, str):
        return {"message": daily_info, "code": 400, "data": None}
    return {
        "message": f"获取{vehicleNo}的日统计信息成功",
        "data": daily_info,
        "code": 200,
    }


@router.get("/onoffline")
async def get_onoffline_data(
    vehicleNo: str,
    startTime: str,  # 时间格式2023-11-01 10:01:01
    endTime: str,  # 时间格式2023-11-01 10:01:01
    curPage: int,
    pageNum: int,
    isAll: Optional[int] = None,
):
    """获取车辆的上下线记录"""
    result = await services.DriverMonitorService.get_dev_onoffline_data(
        vehicleNo=vehicleNo,
        startTime=startTime,
        endTime=endTime,
        curPage=curPage,
        pageNum=pageNum,
        isAll=isAll,
    )
    if isinstance(result, str):
        return {"data": None, "code": 400, "message": result}
    return {"data": result, "code": 200, "message": "success"}


@router.get("/latest_onoffline")
async def get_latest_onoffline_time(vehicleNo: str):
    """获取车辆最新上下线时间"""
    result = await services.DriverMonitorService.get_latest_onoffline_time(vehicleNo)
    if isinstance(result, str):
        return {"data": None, "code": 400, "message": result}
    return {"data": result, "code": 200, "message": "success"}


    