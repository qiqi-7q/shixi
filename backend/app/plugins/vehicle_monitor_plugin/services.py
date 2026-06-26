from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from app.plugins.vehicle_monitor_plugin import models, schemas


class VehicleMonitorService:

    # 创建
    @staticmethod
    async def create_vehicle_monitor(
        db: AsyncSession, monitor: schemas.VehicleMonitorCreate
    ):
        try:
            db_monitor = models.VehicleMonitor(**monitor.model_dump())
            db.add(db_monitor)
            await db.commit()
        except Exception as e:
            await db.rollback()
            return f"创建车辆监测数据失败: {str(e)}"
        await db.refresh(db_monitor)
        return "success"

    # 获取列表
    @staticmethod
    async def get_vehicle_monitors(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        vin_code: Optional[str] = None,
    ):
        filters = [
            models.VehicleMonitor.is_del == False,
        ]
        if vin_code:
            filters.append(models.VehicleMonitor.vin_code.icontains(vin_code))

        # 2. 先查符合条件的总条数（不带分页）
        count_stmt = select(func.count(models.VehicleMonitor.id)).where(*filters)
        total = await db.scalar(count_stmt) or 0

        # 3. 再查分页数据
        data_stmt = (
            select(models.VehicleMonitor)
            .where(*filters)
            .offset(skip)
            .limit(limit)
            .order_by(models.VehicleMonitor.monitor_date.desc())
        )
        result = await db.execute(data_stmt)
        data_list = list(result.scalars().all())

        return {"items": data_list, "total": total, "skip": skip, "limit": limit}

    # 获取单条
    @staticmethod
    async def get_vehicle_monitor(db: AsyncSession, monitor_id: int):
        stmt = await db.execute(
            select(models.VehicleMonitor).where(
                models.VehicleMonitor.id == monitor_id,
                models.VehicleMonitor.is_del == False,
            )
        )
        monitor = stmt.scalar_one_or_none()
        if not monitor:
            return "数据不存在"
        return monitor

    # 更新
    @staticmethod
    async def update_vehicle_monitor(
        db: AsyncSession, monitor_id: int, monitor: schemas.VehicleMonitorUpdate
    ):
        db_monitor = await VehicleMonitorService.get_vehicle_monitor(db, monitor_id)
        if not db_monitor:
            return "数据不存在"
        update_data = monitor.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_monitor, key, value)

        await db.commit()
        await db.refresh(db_monitor)
        return "success"

    # 删除
    @staticmethod
    async def delete_vehicle_monitor(db: AsyncSession, monitor_id: int):
        monitor = await VehicleMonitorService.get_vehicle_monitor(db, monitor_id)
        if not monitor:
            return "数据不存在"
        monitor.is_del = True
        await db.commit()
        return "success"
