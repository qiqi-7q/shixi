import asyncio

from sqlalchemy import exists, select, update

from app.core.database import SessionLocal
from app.plugins.vehicle_plugin.models import Vehicle
from app.plugins.vehicle_monitor_plugin.models import VehicleMonitor
from app.utils.leapcloud_data import call_leapmotor_api
from app.utils.logger import get_logger

logger = get_logger(__name__, log_filename="vehicle_monitor_scheduler.log")


MAX_RETRIES = 3
BASE_DELAY = 2


async def _retry_batch(failed_vins, config_key, api_name):
    """
    批量重试剩余失败的 VIN。
    每轮把整个失败集合一起调 call_leapmotor_api，利用其内部的并发 + 连接池限流；
    本轮成功后只对仍未成功的做下一轮退避重试。
    """
    if not failed_vins:
        return {}, []

    retry_results = {}
    for attempt in range(1, MAX_RETRIES + 1):
        delay = BASE_DELAY * (2 ** (attempt - 1))
        logger.info(
            f"重试 {api_name} 第 {attempt}/{MAX_RETRIES} 次，"
            f"剩 {len(failed_vins)} 个VIN，等待 {delay}s"
        )
        # 等待指定时间
        await asyncio.sleep(delay)

        result, fail = await call_leapmotor_api(failed_vins, config_key=config_key)
        retry_results.update(result)
        if not fail:
            # 本轮全部成功，结束重试
            return retry_results, []
        # 缩小本轮失败集合，下一轮只对仍未成功的重试
        failed_vins = fail

    logger.error(
        f"重试 {api_name} 全部 {MAX_RETRIES} 次后仍有 {len(failed_vins)} 个VIN失败。"
    )
    return retry_results, failed_vins


async def retry_failed_vins(failed_vins, config_key, api_name):
    """批量重试所有失败 VIN（包装层）"""
    if not failed_vins:
        return {}, []
    return await _retry_batch(failed_vins, config_key, api_name)


def _calculate_power_metrics(power_duration: int) -> tuple[float, float]:
    """计算上电时长（小时）和使用率（%）"""
    duration_seconds = power_duration or 0
    duration_hour = duration_seconds / 3600 if duration_seconds else 0
    usage = (duration_seconds / 28800) * 100 if duration_seconds else 0
    return duration_hour, usage


def _find_matching_value(
    target_dt: str, data_list: list, key: str, default: int = 0
) -> int:
    """在数据列表中查找指定日期对应的值"""
    if not data_list:
        return default
    return next((item[key] for item in data_list if item["dt"] == target_dt), default)


def _create_vehicle_monitor_record(
    vin: str, vin_data: dict, dt: str, power_duration: int, distance: int
) -> VehicleMonitor:
    """创建车辆监控记录"""
    duration_hour, usage = _calculate_power_metrics(power_duration)
    return VehicleMonitor(
        vin_code=vin,
        model=vin_data["model"],
        group=vin_data["group"],
        monitor_date=dt,
        power_duration=duration_hour,
        distance=distance,
        usage=usage,
    )


def _process_duration_data(
    vin: str, vin_data: dict, duration: list, mileage: list, add_list: list
) -> None:
    """处理有上电数据的情况"""
    for dura in duration:
        dt = dura["dt"]
        power_duration = dura["on3_duration"] or 0
        distance = _find_matching_value(dt, mileage, "drive_mileage")

        add_list.append(
            _create_vehicle_monitor_record(vin, vin_data, dt, power_duration, distance)
        )


def _process_mileage_only_data(
    vin: str, vin_data: dict, mileage: list, add_list: list
) -> None:
    """处理仅有里程数据的情况"""
    for mile in mileage:
        dt = mile["dt"]
        drive_mileage = mile["drive_mileage"] or 0

        add_list.append(
            _create_vehicle_monitor_record(vin, vin_data, dt, 0, drive_mileage)
        )


async def re_vm_task():
    try:
        logger.info("开始刷新车辆监控数据")
        logger.info("开始从车辆表获取所有VIN码")

        async with SessionLocal() as db:
            vins = await db.execute(
                select(Vehicle.vin_code, Vehicle.model, Vehicle.group).order_by(
                    Vehicle.id.asc()
                )
            )

            vehicles = [
                {
                    "vin_code": row.vin_code,
                    "model": row.model,
                    "group": row.group,
                }
                for row in vins.all()
            ]
            logger.info(f"车辆信息列表(vehicles)： {vehicles}")
            vin_list = [vehicle["vin_code"] for vehicle in vehicles]

            logger.info(f"从车辆表中获取到 {len(vin_list)} 个VIN码")

            logger.info("开始调用LeapCloud API获取车辆监控数据")

            # duration 和 mileage 两个接口并发调用，aiohttp 内部连接池自动限流
            duration_task = asyncio.create_task(
                call_leapmotor_api(vin_list, config_key="duration")
            )
            mileage_task = asyncio.create_task(
                call_leapmotor_api(vin_list, config_key="mileage")
            )
            duration_data, failed_duration_vins = await duration_task
            mileage_data, failed_mileage_vins = await mileage_task

            if failed_duration_vins:
                logger.warning(
                    f"duration 数据获取失败 {len(failed_duration_vins)} 个VIN"
                )
            if failed_mileage_vins:
                logger.warning(f"mileage 数据获取失败 {len(failed_mileage_vins)} 个VIN")

            # 对失败的 VIN 进行重试
            if failed_duration_vins:
                logger.info(
                    f"开始重试 duration 失败的 {len(failed_duration_vins)} 个VIN"
                )
                retry_d, still_failed_d = await retry_failed_vins(
                    failed_duration_vins, "duration", "duration"
                )
                duration_data.update(retry_d)
                if still_failed_d:
                    logger.error(
                        f"duration 重试后仍失败 {len(still_failed_d)} 个VIN: {still_failed_d}"
                    )

            if failed_mileage_vins:
                logger.info(f"开始重试 mileage 失败的 {len(failed_mileage_vins)} 个VIN")
                retry_m, still_failed_m = await retry_failed_vins(
                    failed_mileage_vins, "mileage", "mileage"
                )
                mileage_data.update(retry_m)
                if still_failed_m:
                    logger.error(
                        f"mileage 重试后仍失败 {len(still_failed_m)} 个VIN: {still_failed_m}"
                    )

            # 获取duration_data和mileage_data的并集的vin码
            union_vins = set(duration_data.keys()).union(mileage_data.keys())

            logger.info(
                f"获取车辆监控数据完成,上电数据{len(duration_data)}条，里程数据{len(mileage_data)}条。取并集后共{len(union_vins)}条数据"
            )

            logger.info("开始写入数据库")

            add_list = []

            for vin in union_vins:

                duration = duration_data.get(
                    vin, None
                )  # [{'dt': '2026-06-23','on3_duration': 527.794}，{'dt': '2026-07-01','on3_duration': 527.794}]
                mileage = mileage_data.get(
                    vin, None
                )  # [{'dt': '2026-06-24', 'drive_mileage': 4.7},{'dt': '2026-07-01', 'drive_mileage': 11.8}}]

                vin_data = next(
                    (ve for ve in vehicles if ve["vin_code"] == vin)
                )  # 获取vin对应的车辆信息

                if duration:
                    _process_duration_data(vin, vin_data, duration, mileage, add_list)

                if mileage and duration is None:
                    _process_mileage_only_data(vin, vin_data, mileage, add_list)

            db.add_all(add_list)
            await db.commit()
            logger.info("车辆监控数据写入数据库完成")
    except Exception as ex:
        logger.error(
            f"刷新车辆监控数据时出错，错误信息为:{ex.__traceback__.tb_lineno}:{ex}"
        )
