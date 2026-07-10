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
API_BATCH_SIZE = 50  # 每次调用第三方 API 时的批量大小
DB_WRITE_SIZE = 500  # 每次写入数据库时的批量大小
USAGE_HOURS = 8  # 使用率计算的基准时长，8小时


async def _retry_batch(failed_vins, config_key, api_name):
    """
    批量重试剩余失败的 VIN。
    每轮分批调用 call_leapmotor_api，每批 API_BATCH_SIZE 个 VIN；
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
        await asyncio.sleep(delay)

        batch_result = {}
        batch_failed = []
        total_batches = (len(failed_vins) - 1) // API_BATCH_SIZE + 1
        for i in range(0, len(failed_vins), API_BATCH_SIZE):
            batch = failed_vins[i:i + API_BATCH_SIZE]
            batch_no = i // API_BATCH_SIZE + 1
            logger.info(f"重试 {api_name} 批次 {batch_no}/{total_batches}，共 {len(batch)} 个VIN")
            data, fail = await call_leapmotor_api(batch, config_key=config_key)
            batch_result.update(data)
            batch_failed.extend(fail)

        retry_results.update(batch_result)
        if not batch_failed:
            return retry_results, []
        failed_vins = batch_failed

    logger.warning(
        f"重试 {api_name} 全部 {MAX_RETRIES} 次后仍有 {len(failed_vins)} 个VIN失败。"
    )
    return retry_results, failed_vins


async def _batch_db_write(db, fin_list, batch_size=DB_WRITE_SIZE):
    """分批写入数据库，每批 batch_size 条记录"""
    logger.info(f"第二步，分批写入数据库")
    total = len(fin_list)
    if total == 0:
        return
    total_batches = (total - 1) // batch_size + 1
    for i in range(0, total, batch_size):
        batch = fin_list[i:i + batch_size]
        batch_no = i // batch_size + 1
        db.add_all(batch)
        await db.commit()
        logger.info(
            f"数据库写入批次 {batch_no}/{total_batches}，"
            f"已写入 {min(i + batch_size, total)}/{total} 条"
        )


async def retry_failed_vins(failed_vins, config_key, api_name):
    """批量重试所有失败 VIN（包装层）"""
    if not failed_vins:
        return {}, []
    return await _retry_batch(failed_vins, config_key, api_name)


def _calculate_power_metrics(power_duration: int) -> tuple[float, float]:
    """计算上电时长（小时）和使用率（%）"""
    duration_seconds = power_duration or 0
    duration_hour = duration_seconds / 3600 if duration_seconds else 0
    usage = (duration_seconds / (3600 * USAGE_HOURS)) * 100 if duration_seconds else 0
    return duration_hour, usage


def _find_matching_value(
    target_dt: str, data_list: list, key: str, default: int = 0
) -> int:
    """在数据列表中查找指定日期对应的值"""
    if not data_list:
        return default
    return next((item[key] for item in data_list if item["dt"] == target_dt), default)


def _create_vehicle_monitor_record(item: dict) -> VehicleMonitor:
    """创建车辆监控记录"""
    duration_hour, usage = _calculate_power_metrics(item["power_duration"])
    return VehicleMonitor(
        vin_code=item["vin_code"],
        model=item["model"],
        group=item["group"],
        monitor_date=item["monitor_date"],
        power_duration=duration_hour,
        distance=item["distance"],
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
            {"vin_code":vin, "monitor_date":dt, "model":vin_data["model"], "group":vin_data["group"], "power_duration":power_duration, "distance":distance}
        )


def _process_mileage_only_data(
    vin: str, vin_data: dict, mileage: list, add_list: list
) -> None:
    """处理仅有里程数据的情况"""
    for mile in mileage:
        dt = mile["dt"]
        drive_mileage = mile["drive_mileage"] or 0

        add_list.append(
            {"vin_code":vin, "monitor_date":dt, "model":vin_data["model"], "group":vin_data["group"], "power_duration":0, "distance":drive_mileage}
        )

async def _remove_duplicates(db, add_list: list) -> list:
    """移除在数据库中已存在的记录"""
    # 获取add_list中的日期，去重
    unique_dates = set(item["monitor_date"] for item in add_list)

    # 根据monitor_date和vin_code去重
    existing_records = await db.execute(
        select(VehicleMonitor.vin_code, VehicleMonitor.monitor_date).where(
            VehicleMonitor.monitor_date.in_(unique_dates),
        )
    )
    # 数据库中已存在的记录 (id, vin_code, monitor_date, power_duration, distance)
    existing_records = set(
        (item.vin_code, item.monitor_date.strftime("%Y-%m-%d")) for item in existing_records.all()
    )

    # 过滤出不存在的记录
    fin_list = [
        item for item in add_list
        if (item["vin_code"], item["monitor_date"]) not in existing_records
    ]
    return fin_list


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
            vin_list = [vehicle["vin_code"] for vehicle in vehicles]

            logger.info(f"车辆信息获取成功，从车辆表中获取到 {len(vin_list)} 个VIN码")

            logger.info("开始调用LeapCloud API获取车辆监控数据")

            # 分批调用，每批 API_BATCH_SIZE 个 VIN，duration 和 mileage 并发请求
            duration_data = {}
            mileage_data = {}
            failed_duration_vins = []
            failed_mileage_vins = []
            total_batches = (len(vin_list) - 1) // API_BATCH_SIZE + 1
            for i in range(0, len(vin_list), API_BATCH_SIZE):
                batch = vin_list[i:i + API_BATCH_SIZE]
                batch_no = i // API_BATCH_SIZE + 1
                logger.info(f"API 批次 {batch_no}/{total_batches}，共 {len(batch)} 个VIN")
                d_res, m_res = await asyncio.gather(
                    call_leapmotor_api(batch, config_key="duration"),
                    call_leapmotor_api(batch, config_key="mileage")
                )
                d, fd = d_res
                m, fm = m_res
                duration_data.update(d)
                mileage_data.update(m)
                failed_duration_vins.extend(fd)
                failed_mileage_vins.extend(fm)

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
                    logger.warning(
                        f"duration 重试后仍失败 {len(still_failed_d)} 个VIN"
                    )

            if failed_mileage_vins:
                logger.info(f"开始重试 mileage 失败的 {len(failed_mileage_vins)} 个VIN")
                retry_m, still_failed_m = await retry_failed_vins(
                    failed_mileage_vins, "mileage", "mileage"
                )
                mileage_data.update(retry_m)
                if still_failed_m:
                    logger.warning(
                        f"mileage 重试后仍失败 {len(still_failed_m)} 个VIN"
                    )

            # 获取duration_data和mileage_data的并集的vin码
            union_vins = set(duration_data.keys()).union(mileage_data.keys())

            logger.info(
                f"获取车辆监控数据完成,上电数据{len(duration_data)}条，里程数据{len(mileage_data)}条。取并集后共{len(union_vins)}条数据"
            )

            logger.info("开始写入数据库，第一步去重")

            add_list = []

            for vin in union_vins:

                duration = duration_data.get(
                    vin, None
                )
                mileage = mileage_data.get(
                    vin, None
                )

                vin_data = next(
                    (ve for ve in vehicles if ve["vin_code"] == vin)
                )  # 获取vin对应的车辆信息

                if duration:
                    _process_duration_data(vin, vin_data, duration, mileage, add_list)

                if mileage and duration is None:
                    _process_mileage_only_data(vin, vin_data, mileage, add_list)

            # 去重
            fin_list = await _remove_duplicates(db, add_list)
            logger.info(f"共查出{len(add_list)}条数据，过滤已存在的数据后，需要新增{len(fin_list)}条数据")

            # 新增
            fin_add_list = [_create_vehicle_monitor_record(item) for item in fin_list]
            await _batch_db_write(db, fin_add_list)
            logger.info("车辆监控数据写入数据库完成\n")
    except Exception as ex:
        logger.error(
            f"刷新车辆监控数据时出错，位置为第{ex.__traceback__.tb_lineno}行，错误信息:{ex}\n"
        )