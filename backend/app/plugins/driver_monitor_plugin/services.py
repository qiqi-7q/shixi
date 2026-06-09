from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.plugins.driver_monitor_plugin import models, schemas


class DriverMonitorService:

    @staticmethod
    async def monitor_check(db: AsyncSession, monitor) -> str | None:
        if not monitor:
            return "Monitor is missing"
        if not monitor.test_date:
            return "Test date is missing"
        if not monitor.test_start_time or not monitor.test_end_time:
            return "Test start time or test end time is missing"
        if not monitor.vin_code:
            return "VIN code is missing"
        if not monitor.driver_name:
            return "Driver name is missing"
        if not monitor.dms_trigger_count:
            return "DMS trigger count is missing"
        if not monitor.power_start_duration or not monitor.power_end_duration:
            return "Power start duration or power end duration is missing"
        if not monitor.distance:
            return "Distance is missing"
        vinExisting = await db.execute(
            select(models.DriverMonitor).where(
                models.DriverMonitor.vin_code == monitor.vin_code
            )
        )
        if vinExisting.scalars().first():
            return "vin_code already exists"

    # 创建
    @staticmethod
    async def create_driver_monitor(
        db: AsyncSession, monitor: schemas.DriverMonitorCreate
    ):
        check = await DriverMonitorService.monitor_check(db, monitor)
        if check:
            return check
        db_monitor = models.DriverMonitor(**monitor.model_dump())
        db.add(db_monitor)
        await db.commit()
        await db.refresh(db_monitor)
        return "success"

    # 获取列表
    @staticmethod
    async def get_driver_monitors(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        driver_name: Optional[str] = None,
        vin_code: Optional[str] = None,
        test_start_date: Optional[date] = None,
        test_end_date: Optional[date] = None,
    ):
        query = select(models.DriverMonitor)
        if driver_name:
            query = query.filter(models.DriverMonitor.driver_name.contains(driver_name))
        if vin_code:
            query = query.filter(models.DriverMonitor.vin_code == vin_code)
        if test_start_date:
            query = query.filter(models.DriverMonitor.test_date >= test_start_date)
        if test_end_date:
            query = query.filter(models.DriverMonitor.test_date <= test_end_date)
        result_v1 = query.offset(skip).limit(limit)
        result = await db.execute(result_v1)
        return list(result.scalars().all())

    # 获取单条
    @staticmethod
    async def get_driver_monitor(db: AsyncSession, monitor_id: int):
        monitor = await db.get(models.DriverMonitor, monitor_id)
        if not monitor:
            return "monitor not found"
        return monitor

    # 更新
    @staticmethod
    async def update_driver_monitor(
        db: AsyncSession, monitor_id: int, monitor: schemas.DriverMonitorUpdate
    ):
        db_monitor = await db.get(models.DriverMonitor, monitor_id)
        if not db_monitor:
            return "monitor not found"
        vinExisting = await db.execute(
            select(models.DriverMonitor).where(
                models.DriverMonitor.vin_code == monitor.vin_code
            )
        )
        if vinExisting.scalars().first():
            return "vin_code already exists"
        update_data = monitor.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_monitor, key, value)

        await db.commit()
        await db.refresh(db_monitor)
        return "success"

    # 删除
    @staticmethod
    async def delete_driver_monitor(db: AsyncSession, monitor_id: int):
        monitor = await db.get(models.DriverMonitor, monitor_id)
        if not monitor:
            return "monitor not found"
        await db.delete(monitor)
        await db.commit()
        return "success"
