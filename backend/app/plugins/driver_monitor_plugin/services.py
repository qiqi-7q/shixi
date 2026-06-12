from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from app.plugins.driver_monitor_plugin import models, schemas


class DriverMonitorService:

    @staticmethod
    async def monitor_check(db: AsyncSession, monitor) -> str | None:
        if not monitor:
            return "驾驶员监测信息不能为空"
        if not monitor.test_date:
            return "日期不能为空"
        if not monitor.test_start_time or not monitor.test_end_time:
            return "测试时间不能为空"
        if not monitor.vin_code:
            return "测试车辆VIN号不能为空"
        if not monitor.driver_name:
            return "司机姓名不能为空"
        if not monitor.dms_trigger_count:
            return "DMS触发次数不能为空"
        if not monitor.power_start_duration or not monitor.power_end_duration:
            return "车辆上电时间段不能为空"
        if not monitor.distance:
            return "行驶里程不能为空"
        vinExisting = await db.execute(
            select(models.DriverMonitor).where(
                models.DriverMonitor.vin_code == monitor.vin_code
            )
        )
        if vinExisting.scalars().first():
            return "测试车辆VIN号已存在"

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
        driver_status : Optional[str] = None
    ):
        filters = []
        if vin_code:
            filters.append(models.DriverMonitor.vin_code == vin_code)
        if driver_status:
            filters.append(models.DriverMonitor.driver_status == driver_status)
        if driver_name:
            filters.append(models.DriverMonitor.driver_name.contains(driver_name))
        if test_start_date:
            filters.append(models.DriverMonitor.test_date >= test_start_date)
        if test_end_date:
            filters.append(models.DriverMonitor.test_date <= test_end_date)

        # 2. 先查符合条件的总条数（不带分页）
        count_stmt = select(func.count(models.DriverMonitor.id)).where(*filters)
        total = await db.scalar(count_stmt) or 0

        # 3. 再查分页数据
        data_stmt = (
            select(models.DriverMonitor)
            .where(*filters)
            .offset(skip)
            .limit(limit)
            .order_by(models.DriverMonitor.id.desc())
        )
        result = await db.execute(data_stmt)
        data_list = list(result.scalars().all())
        
        return {
            "items": data_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    # 获取单条
    @staticmethod
    async def get_driver_monitor(db: AsyncSession, monitor_id: int):
        monitor = await db.get(models.DriverMonitor, monitor_id)
        if not monitor:
            return "数据不存在"
        return monitor

    # 更新
    @staticmethod
    async def update_driver_monitor(
        db: AsyncSession, monitor_id: int, monitor: schemas.DriverMonitorUpdate
    ):
        db_monitor = await db.get(models.DriverMonitor, monitor_id)
        if not db_monitor:
            return "数据不存在"
        vinExisting = await db.execute(
            select(models.DriverMonitor).where(
                models.DriverMonitor.vin_code == monitor.vin_code,
                models.DriverMonitor.id != monitor_id
            )
        )
        if vinExisting.scalars().first():
            return "测试车辆VIN号已存在"
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
            return "数据不存在"
        await db.delete(monitor)
        await db.commit()
        return "success"

    # ========== 统计接口 ==========
    
    # 获取监控概览统计
    @staticmethod
    async def get_monitor_overview(db: AsyncSession, start_date: Optional[date] = None, end_date: Optional[date] = None, driver_name: Optional[str] = None, driver_status: Optional[str] = None):
        """获取监控概览统计数据"""
        # 构建筛选条件
        filters = []
        if driver_name:
            filters.append(models.DriverMonitor.driver_name == driver_name)
        if driver_status:
            filters.append(models.DriverMonitor.driver_status == driver_status)
        if start_date:
            filters.append(models.DriverMonitor.test_date >= start_date)
        if end_date:
            filters.append(models.DriverMonitor.test_date <= end_date)
        
        # 统计总数
        total_stmt = select(func.count(models.DriverMonitor.id)).where(*filters)
        total = await db.scalar(total_stmt) or 0
        
        # 统计各状态数量（使用相同的筛选条件）
        status_stmt = select(
            models.DriverMonitor.driver_status,
            func.count(models.DriverMonitor.id)
        ).where(*filters).group_by(models.DriverMonitor.driver_status)
        status_result = await db.execute(status_stmt)
        status_counts = {row[0].value: row[1] for row in status_result.all()}
        
        # 确保所有状态都返回
        all_statuses = ["正常", "疲劳", "轻微疲劳", "严重疲劳"]
        
        return {
            "total": total,
            "status_counts": [{"status": status, "count": status_counts.get(status, 0)} for status in all_statuses]
        }

    # 获取每日疲劳状态统计
    @staticmethod
    async def get_daily_fatigue_count(db: AsyncSession, start_date: Optional[date] = None, end_date: Optional[date] = None, driver_name: Optional[str] = None, driver_status: Optional[str] = None):
        """获取每日出现疲劳状态的司机数量"""
        stmt = select(
            func.date(models.DriverMonitor.test_date).label('date'),
            func.count(models.DriverMonitor.id).label('count')
        )
        
        # 筛选疲劳状态
        stmt = stmt.filter(
            models.DriverMonitor.driver_status.in_(
                [models.DriverStatus.FATIGUE, models.DriverStatus.MILDFAIR, models.DriverStatus.SEVEREFATIGUE]
            )
        )
        
        # 动态筛选条件
        if driver_name:
            stmt = stmt.filter(models.DriverMonitor.driver_name == driver_name)
        if driver_status:
            stmt = stmt.filter(models.DriverMonitor.driver_status == driver_status)
        if start_date:
            stmt = stmt.filter(models.DriverMonitor.test_date >= start_date)
        if end_date:
            stmt = stmt.filter(models.DriverMonitor.test_date <= end_date)
        
        stmt = stmt.group_by(func.date(models.DriverMonitor.test_date)).order_by(func.date(models.DriverMonitor.test_date))
        
        result = await db.execute(stmt)
        return [{"date": str(row.date), "count": row.count} for row in result.all()]

    # 获取每日DMS触发次数统计
    @staticmethod
    async def get_daily_dms_count(db: AsyncSession, start_date: Optional[date] = None, end_date: Optional[date] = None, driver_name: Optional[str] = None, driver_status: Optional[str] = None):
        """获取每日DMS触发次数"""
        stmt = select(
            func.date(models.DriverMonitor.test_date).label('date'),
            func.sum(models.DriverMonitor.dms_trigger_count).label('total_count')
        )
        
        # 动态筛选条件
        if driver_name:
            stmt = stmt.filter(models.DriverMonitor.driver_name == driver_name)
        if driver_status:
            stmt = stmt.filter(models.DriverMonitor.driver_status == driver_status)
        if start_date:
            stmt = stmt.filter(models.DriverMonitor.test_date >= start_date)
        if end_date:
            stmt = stmt.filter(models.DriverMonitor.test_date <= end_date)
        
        stmt = stmt.group_by(func.date(models.DriverMonitor.test_date)).order_by(func.date(models.DriverMonitor.test_date))
        
        result = await db.execute(stmt)
        return [{"date": str(row.date), "total_count": row.total_count or 0} for row in result.all()]

    # 获取司机疲劳次数统计
    @staticmethod
    async def get_driver_fatigue_count(db: AsyncSession, start_date: Optional[date] = None, end_date: Optional[date] = None, driver_name: Optional[str] = None, driver_status: Optional[str] = None):
        """按司机统计疲劳次数"""
        stmt = select(
            models.DriverMonitor.driver_name.label('driver_name'),
            func.count(models.DriverMonitor.id).label('fatigue_count')
        )
        
        # 筛选疲劳状态
        stmt = stmt.filter(
            models.DriverMonitor.driver_status.in_(
                [models.DriverStatus.FATIGUE, models.DriverStatus.MILDFAIR, models.DriverStatus.SEVEREFATIGUE]
            )
        )
        
        # 动态筛选条件
        if driver_name:
            stmt = stmt.filter(models.DriverMonitor.driver_name == driver_name)
        if driver_status:
            stmt = stmt.filter(models.DriverMonitor.driver_status == driver_status)
        if start_date:
            stmt = stmt.filter(models.DriverMonitor.test_date >= start_date)
        if end_date:
            stmt = stmt.filter(models.DriverMonitor.test_date <= end_date)
        
        stmt = stmt.group_by(models.DriverMonitor.driver_name).order_by(func.count(models.DriverMonitor.id).desc())
        
        result = await db.execute(stmt)
        return [{"driver_name": row.driver_name, "fatigue_count": row.fatigue_count} for row in result.all()]

    # 获取状态分布统计
    @staticmethod
    async def get_status_distribution(db: AsyncSession, start_date: Optional[date] = None, end_date: Optional[date] = None, driver_name: Optional[str] = None, driver_status: Optional[str] = None):
        """获取司机状态分布统计"""
        stmt = select(
            models.DriverMonitor.driver_status.label('status'),
            func.count(models.DriverMonitor.id).label('count')
        )
        
        # 动态筛选条件
        if driver_name:
            stmt = stmt.filter(models.DriverMonitor.driver_name == driver_name)
        # driver_status 参数在这里主要用于筛选特定状态的记录
        # 但状态分布本身就是按状态分组，所以如果指定了 driver_status，结果只会包含该状态
        if driver_status:
            stmt = stmt.filter(models.DriverMonitor.driver_status == driver_status)
        if start_date:
            stmt = stmt.filter(models.DriverMonitor.test_date >= start_date)
        if end_date:
            stmt = stmt.filter(models.DriverMonitor.test_date <= end_date)
        
        stmt = stmt.group_by(models.DriverMonitor.driver_status)
        
        result = await db.execute(stmt)
        status_counts = {row.status.value: row.count for row in result.all()}
        
        # 确保所有状态都返回
        all_statuses = ["正常", "疲劳", "轻微疲劳", "严重疲劳"]
        return [{"status": status, "count": status_counts.get(status, 0)} for status in all_statuses]
