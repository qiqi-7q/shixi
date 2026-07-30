from app.utils.logger import get_logger
from app.core.database import SessionLocal
from sqlalchemy import select, update
from app.plugins.vehicle_plugin.models import Vehicle
from datetime import date, timedelta
from app.plugins.driver_monitor_plugin.models import MonitorInfo

from app.plugins.driver_monitor_plugin.services import DriverMonitorService

logger = get_logger(__name__, log_filename="driver_monitor_scheduler.log")

API_BATCH_SIZE = 50  # 每次调用第三方 API 时的批量大小
DB_WRITE_SIZE = 500  # 每次写入数据库的批量大小
PREVIOUS_DAYS = 1  # 同步某一天的监控数据，以今日日期为基准


def _find_matching_value(
    target: str | int, data_list: list, field: str, default: dict = {}
) -> dict:
    """在数据列表中查找指定字段对应的数据，跳过列表中的None值"""
    if not data_list:
        return default
    return next(
        (item for item in data_list if item is not None and item[field] == target),
        default,
    )


async def _batch_db_write(db, fin_list, batch_size=DB_WRITE_SIZE):
    """分批写入数据库，每批 batch_size 条记录"""
    logger.info(f"第四步，分批写入数据库")
    total = len(fin_list)
    if total == 0:
        return
    total_batches = (total - 1) // batch_size + 1
    for i in range(0, total, batch_size):
        batch = fin_list[i : i + batch_size]
        batch_no = i // batch_size + 1
        db.add_all(batch)
        await db.commit()
        logger.info(
            f"数据库写入批次 {batch_no}/{total_batches}，"
            f"已写入 {min(i + batch_size, total)}/{total} 条"
        )


async def sync_monitor_data():
    """同步监控数据"""
    try:
        async with SessionLocal() as db:

            today_date = date.today()
            test_date = today_date - timedelta(days=PREVIOUS_DAYS)
            hms_date_start = test_date.strftime("%Y-%m-%d 00:00:00")
            hms_date_end = test_date.strftime("%Y-%m-%d 23:59:59")
            ym_date = test_date.strftime("%Y-%m")
            ymd_date_str = test_date.strftime("%Y%m%d")

            logger.info(f"开始同步监控数据，测试日期为：{test_date}")
            logger.info("第一步，从车辆资源表获取所有车辆VIN码")

            vins = await db.execute(select(Vehicle.vin_code).order_by(Vehicle.id.asc()))
            vin_list = vins.scalars().all()
            logger.info(
                f"车辆信息获取成功，从车辆资源表中获取到 {len(vin_list)} 个VIN码"
            )

            logger.info(f"第二步，从监控信息表获取测试日期对应的记录")
            existing_records = await db.execute(
                select(MonitorInfo.vin_code).where(
                    MonitorInfo.test_date == test_date,
                )
            )
            existing_vins = set(item.vin_code for item in existing_records.all())
            logger.info(f"监控信息表中测试日期存在 {len(existing_vins)} 条记录")

            logger.info(f"第三步，从智驾车联网平台获取所有车辆的监控数据并处理")

            car_info = await DriverMonitorService.get_car_info()
            if isinstance(car_info, str):
                logger.error(f"获取车辆监控数据失败: {car_info}")
                car_info = []
            logger.info(
                f"获取智驾车联网平台车辆基础信息成功，共 {len(car_info)} 条记录"
            )

            add_list = []
            exist_num = 0
            # 从智驾联网平台获取监控数据
            for i in range(0, len(vin_list), API_BATCH_SIZE):
                batch_vin_list = vin_list[i : i + API_BATCH_SIZE]
                logger.info(
                    f"正在获取第 {i // API_BATCH_SIZE + 1}/{len(vin_list) // API_BATCH_SIZE + 1} 批次的监控数据"
                )
                for vin in batch_vin_list:
                    # 去重，避免重复写入
                    if vin in existing_vins:
                        exist_num += 1
                        continue

                    match_car_info = _find_matching_value(
                        target=vin, data_list=car_info, field="vehicleNo"
                    )
                    # 未匹配到车辆信息，跳过
                    if not match_car_info:
                        continue

                    device_code = match_car_info["deviceNo"]

                    alarm_data = await DriverMonitorService.get_alarm_data(
                        startTime=hms_date_start,
                        endTime=hms_date_end,
                        handleStatus=0,
                        isAll=True,
                        curPage=1,
                        pageNum=10,
                        alarmTypes=[1, 2, 3, 4, 5, 6, 7, 8],
                        vehicleNo=vin,
                    )

                    # 报警类型映射: alarmType -> 变量名
                    ALARM_TYPE_MAP = {
                        1: "fatigue",
                        2: "calling",
                        3: "smoke",
                        4: "distract",
                        5: "abnormal",
                        6: "snapshot",
                        7: "driver_change",
                        8: "no_belt",
                    }
                    alarm_counts = {name: 0 for name in ALARM_TYPE_MAP.values()}

                    if alarm_data and "total" in alarm_data and alarm_data["total"] > 0:
                        for alarm in alarm_data["dataList"]:
                            field = ALARM_TYPE_MAP.get(alarm["alarmType"])
                            if field:
                                alarm_counts[field] += 1

                    daily_info = await DriverMonitorService.get_daily_info(
                        dateTime=ym_date,
                        vehicleNo=vin,
                    )

                    match_daily_infos = daily_info[0] if daily_info else {}
                    match_info = (
                        match_daily_infos["dailyInfo"]
                        if match_daily_infos and "dailyInfo" in match_daily_infos
                        else []
                    )
                    match_daily_info = _find_matching_value(
                        target=int(ymd_date_str), data_list=match_info, field="dateTime"
                    )

                    mileage = (
                        (
                            match_daily_info["endMileage"]
                            - match_daily_info["startMileage"]
                        )
                        / 1000
                        if match_daily_info
                        else 0
                    )
                    # max_speed = (
                    #     match_daily_info["maxSpeed"] / 10 if match_daily_info else 0
                    # )
                    # avg_speed = (
                    #     (mileage * 3600) / match_daily_info["driveTimeLen"]
                    #     if match_daily_info
                    #     else 0
                    # )

                    onoffline_datas = await DriverMonitorService.get_dev_onoffline_data(
                        vehicleNo=vin,
                        startTime=hms_date_start,
                        endTime=hms_date_end,
                        curPage=1,
                        pageNum=10,
                        isAll=1,
                    )
                    # 当日上电时长（秒）
                    duration = 0
                    if onoffline_datas and "dataList" in onoffline_datas:
                        onoffline_data = onoffline_datas["dataList"]
                    else:
                        onoffline_data = []

                    for item in onoffline_data:
                        if "isOnline" not in item or item["isOnline"] == False:
                            duration += item["timeLen"]
                        else:
                            continue

                    add_list.append(
                        MonitorInfo(
                            test_date=test_date,
                            vin_code=vin,
                            device_code=device_code,
                            fatigue=alarm_counts["fatigue"],
                            calling=alarm_counts["calling"],
                            smoke=alarm_counts["smoke"],
                            distract=alarm_counts["distract"],
                            abnormal=alarm_counts["abnormal"],
                            snapshot=alarm_counts["snapshot"],
                            driver_change=alarm_counts["driver_change"],
                            no_belt=alarm_counts["no_belt"],
                            mileage=round(mileage, 1),
                            # max_speed=round(max_speed, 1),
                            # avg_speed=round(avg_speed, 1),
                            duration=duration,
                        )
                    )

            logger.info(
                f"获取智驾联网平台监控数据成功，共 {len(add_list)} 条记录，{exist_num} 条数据库中已存在"
            )

            if add_list:
                await _batch_db_write(db, add_list)
                logger.info(f"监控数据同步到数据库完成\n")
            else:
                logger.info("没有数据需要写入数据库\n")

    except Exception as ex:
        logger.error(
            f"同步监控数据失败，错误位置为第{ex.__traceback__.tb_lineno}行，错误信息:{ex}\n"
        )
