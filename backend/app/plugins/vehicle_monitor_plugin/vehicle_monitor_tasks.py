import asyncio
from datetime import date
import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy import exists, select, update
from app.core.config import settings
from app.core.database import SessionLocal
from app.plugins.vehicle_plugin.models import Vehicle
from app.plugins.vehicle_monitor_plugin.models import VehicleMonitor
from app.utils.leapcloud_data import call_leapmotor_api

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# 使用 settings.BASE_DIR 获取项目根目录
# 配置日志记录器，将日志写入vehicle_monitor_scheduler.log文件,路径为logs/vehicle_monitor_scheduler.log
if not logger.handlers:
    # 确保日志目录存在
    settings.LOG_DIR.mkdir(exist_ok=True, parents=True)
    log_file = settings.LOG_DIR / "vehicle_monitor_scheduler.log"

    try:
        # 单个日志最大10MB，最多保留10个归档日志
        handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=10, encoding="utf-8"
        )
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(funcName)s - %(levelname)s - %(message)s"
            )
        )  # 设置日志格式，包含时间、接口名称(如，refresh_vehicle_status_task)、级别和信息
        logger.addHandler(handler)  # 将文件处理器添加到日志记录器中
    except Exception as e:
        logger.error(f"无法创建vehicle_monitor.log日志文件，错误信息为: {e}")


BATCH_SIZE = 60
MAX_RETRIES = 3
BASE_DELAY = 2


async def retry_failed_vins(failed_vins, config_key, api_name):
    retry_results = {}
    still_failed = []

    for vin in failed_vins:
        success = False
        for attempt in range(1, MAX_RETRIES + 1):
            delay = BASE_DELAY * (2 ** (attempt - 1))
            logger.info(
                f"重试 {api_name} VIN={vin}，第 {attempt}/{MAX_RETRIES} 次，等待 {delay}s"
            )
            # 等待指定时间
            await asyncio.sleep(delay)

            result, _ = call_leapmotor_api([vin], config_key=config_key)
            if vin in result:
                retry_results[vin] = result[vin]
                logger.info(f"重试 {api_name} VIN={vin} 成功")
                success = True
                break
            else:
                logger.warning(f"重试 {api_name} VIN={vin} 第 {attempt} 次失败")

        if not success:
            still_failed.append(vin)
            logger.error(f"重试 {api_name} VIN={vin} 全部 {MAX_RETRIES} 次失败，已放弃")

    return retry_results, still_failed


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
                    "vin_code": vin["vin_code"],
                    "model": vin["model"],
                    "group": vin["group"],
                }
                for vin in vins.mappings().all()
            ]

            vin_list = [vehicle["vin_code"] for vehicle in vehicles]

            logger.info(f"从车辆表中获取到 {len(vin_list)} 个VIN码")

            logger.info("开始分片批量调用LeapCloud API获取车辆监控数据")
            duration_data = {}
            mileage_data = {}
            failed_duration_vins = []
            failed_mileage_vins = []
            # 计算总批次数
            total_batches = (len(vin_list) + BATCH_SIZE - 1) // BATCH_SIZE

            # 分片处理，i为当前批次的起始索引，BATCH_SIZE为每个批次的VIN数量
            for i in range(0, len(vin_list), BATCH_SIZE):
                batch = vin_list[i : i + BATCH_SIZE]
                batch_num = i // BATCH_SIZE + 1
                logger.info(
                    f"处理第 {batch_num}/{total_batches} 批，共 {len(batch)} 个VIN"
                )

                batch_duration, failed_duration = call_leapmotor_api(
                    batch, config_key="duration"
                )
                duration_data.update(batch_duration)
                failed_duration_vins.extend(failed_duration)
                if failed_duration:
                    logger.warning(
                        f"第 {batch_num} 批 duration 数据获取失败 {len(failed_duration)} 个VIN: {failed_duration}"
                    )

                batch_mileage, failed_mileage = call_leapmotor_api(
                    batch, config_key="mileage"
                )
                mileage_data.update(batch_mileage)
                failed_mileage_vins.extend(failed_mileage)
                if failed_mileage:
                    logger.warning(
                        f"第 {batch_num} 批 mileage 数据获取失败 {len(failed_mileage)} 个VIN: {failed_mileage}"
                    )

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

                duration = duration_data.get(vin, None)
                # [{'vin': 'LFZ63AC55TH000216', 'dt': '2026-06-28', 'on3_cnt': 2, 'on3_duration': 527.908}]}
                power_duration = duration[0]["on3_duration"] if duration else 0
                duration_hour = power_duration / 3600 if power_duration else 0
                usage = min(
                    (power_duration / 28800) * 100 if power_duration else 0, 100
                )

                mileage = mileage_data.get(vin, None)
                # [{'vin': 'LFZ93AA94TD000265', 'dt': '2026-06-28', 'drive_mileage': 45.0}]
                distance = mileage[0]["drive_mileage"] if mileage else 0
                monitor_date = duration[0]["dt"] if duration else mileage[0]["dt"]

                vin_data = next((ve for ve in vehicles if ve["vin_code"] == vin))

                add_list.append(
                    VehicleMonitor(
                        vin_code=vin,
                        model=vin_data["model"],
                        group=vin_data["group"],
                        monitor_date=monitor_date,
                        power_duration=duration_hour,
                        distance=distance,
                        usage=usage,
                    )
                )

            db.add_all(add_list)
            await db.commit()
            logger.info("车辆监控数据写入数据库完成")
    except Exception as ex:
        logger.error(f"刷新车辆监控数据时出错，错误信息为: {ex}")
