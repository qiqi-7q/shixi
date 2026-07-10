from datetime import date
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from app.plugins.vehicle_monitor_plugin import models, schemas
from app.plugins.vehicle_plugin.models import Vehicle

from app.utils.build_condition import build_condition


class VehicleMonitorService:

    # 获取单条
    @staticmethod
    async def get_vehicle_monitor(db: AsyncSession, monitor_id: int):
        stmt = await db.execute(
            select(models.VehicleMonitor).where(
                models.VehicleMonitor.is_del == 0,
                models.VehicleMonitor.id == monitor_id,
            )
        )
        monitor = stmt.scalar_one_or_none()
        if not monitor:
            return "数据不存在"
        return monitor

    @staticmethod
    async def get_vehicle_monitors(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        conditions: Optional[List[dict]] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> dict:
        stmt = select(models.VehicleMonitor)
        if conditions:
            get_condition = []

            for cond in conditions:
                field_name = cond["advanced_field"]
                operator = cond["advanced_operator"]
                value = cond["advanced_value"]

                condition = build_condition(
                    models.VehicleMonitor, field_name, operator, value
                )
                if condition is not None:
                    get_condition.append(condition)

            # 应用查询条件
            stmt = stmt.where(and_(*get_condition))

        # 统计总数
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(total_stmt)
        total = total_result.scalar_one()

        # 1. 前置统一处理排序参数，消除分支差异逻辑
        # 默认排序字段、升降序
        default_sort = "id"
        default_desc = True
        sort_expr = None

        # 处理空排序场景
        if not sort_by:
            sort_by = default_sort
            is_desc = default_desc
        else:
             # 字段白名单校验
            if sort_by not in schemas.VEHICLE_MONITOR_WHITELIST:
                sort_by = "model"
            # 校验排序方向
            valid_order = sort_order.lower() if sort_order else "asc"
            is_desc = valid_order == "desc" if valid_order in ("asc", "desc") else False

        sort_expr = getattr(models.VehicleMonitor, sort_by)

        # 升降序统一处理
        order_clause = sort_expr.desc() if is_desc else sort_expr.asc()
        stmt = stmt.order_by(order_clause).offset(skip).limit(limit)

        # 3. 查询逻辑全局只写一次，无重复
        result = await db.execute(stmt)
        data_list = list(result.scalars().all())
        return {
            "items": data_list,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    async def get_vin_list(
        db: AsyncSession,
    ):
        # 分页，只返回前30条数据
        stmt = await db.execute(
            select(Vehicle.vin_code).distinct().limit(20)
        )
        return list(stmt.scalars().all())

    @staticmethod
    async def get_cars_info(
        db: AsyncSession,
        vin_code: str,
    ) -> list[dict]:
        filters = [
            models.VehicleMonitor.is_del == 0,
        ]
        if vin_code:
            filters.append(models.VehicleMonitor.vin_code == vin_code)

        stmt = await db.execute(
            select(
                models.VehicleMonitor.vin_code,
                models.VehicleMonitor.power_duration,
                models.VehicleMonitor.usage,
                models.VehicleMonitor.distance,
                models.VehicleMonitor.monitor_date,
            )
            .where(*filters)
            .order_by(models.VehicleMonitor.monitor_date.asc())
        )

        car_info_dict = stmt.all()

        if not car_info_dict:
            return []
        car_info = [
            {
                "vin_code": record.vin_code,
                "power_duration": record.power_duration,
                "usage": record.usage,
                "distance": record.distance,
                "monitor_date": record.monitor_date,
            }
            for record in car_info_dict
        ]

        return car_info

    @staticmethod
    async def get_groups(
        db: AsyncSession,
        model: Optional[str] = None,
    ) -> list[dict]:
        filters = [
            models.VehicleMonitor.is_del == 0,
        ]
        if model:
            filters.append(models.VehicleMonitor.model == model)

        stmt = (
            select(
                models.VehicleMonitor.group,
                models.VehicleMonitor.monitor_date,
                func.avg(models.VehicleMonitor.usage).label("avg_usage"),
                func.count(models.VehicleMonitor.id).label("count"),
            )
            .where(*filters)
            .group_by(models.VehicleMonitor.group, models.VehicleMonitor.monitor_date)
            .order_by(
                models.VehicleMonitor.monitor_date.asc(),
                models.VehicleMonitor.group.asc(),
            )
        )

        result = await db.execute(stmt)
        rows = result.all()

        groups = []
        for row in rows:
            groups.append(
                {
                    "group": row.group,
                    "monitor_date": row.monitor_date,
                    "avg_usage": round(float(row.avg_usage), 2),
                    "count": row.count,
                }
            )

        return groups

    @staticmethod
    async def get_usages(
        db: AsyncSession,
        model: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:
        print("start_date",start_date,end_date)
        filters = [
            models.VehicleMonitor.is_del == 0,
        ]
        if model:
            if "," in model:
                values = [v.strip() for v in model.split(",") if v.strip()]
                filters.append(models.VehicleMonitor.model.in_(values))
            if "," not in model:
                filters.append(models.VehicleMonitor.model == model)
        if start_date:
            filters.append(models.VehicleMonitor.monitor_date >= start_date)
        if end_date:
            filters.append(models.VehicleMonitor.monitor_date <= end_date)
        # 据VIN统计单车的平均使用率
        stmt = await db.execute(
            select(
                models.VehicleMonitor.vin_code,
                func.AVG(models.VehicleMonitor.usage).label("avg_usage"),
            )
            .where(*filters)
            .group_by(models.VehicleMonitor.vin_code)
            .order_by(func.AVG(models.VehicleMonitor.usage).desc())
        )
        usages_dict = stmt.all()

        if not usages_dict:
            return []
        usage_info = [
            {
                "vin_code": record.vin_code,
                "avg_usage": round(float(record.avg_usage), 2),
            }
            for record in usages_dict
        ]

        return usage_info

    @staticmethod
    async def get_distences(
        db: AsyncSession,
        model: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:
        filters = [
            models.VehicleMonitor.is_del == 0,
        ]
        if model:
            if "," in model:
                values = [v.strip() for v in model.split(",") if v.strip()]
                filters.append(models.VehicleMonitor.model.in_(values))
            if "," not in model:
                filters.append(models.VehicleMonitor.model == model)
        if start_date and end_date:
            filters.append(models.VehicleMonitor.monitor_date >= start_date)
        if end_date:
            filters.append(models.VehicleMonitor.monitor_date <= end_date)
        stmt = await db.execute(
            select(
                models.VehicleMonitor.vin_code,
                func.AVG(models.VehicleMonitor.distance).label("avg_distance"),
            )
            .where(*filters)
            .group_by(models.VehicleMonitor.vin_code)
            .order_by(func.AVG(models.VehicleMonitor.distance).desc())
        )
        distances_dict = stmt.all()

        if not distances_dict:
            return []

        distance_info = [
            {
                "vin_code": record.vin_code,
                "avg_distance": round(float(record.avg_distance), 2),
            }
            for record in distances_dict
        ]

        return distance_info

    @staticmethod
    async def get_vin(db: AsyncSession) -> list[dict]:
        stmt = await db.execute(
            select(
                models.VehicleMonitor.vin_code,
                func.count(models.VehicleMonitor.id).label("count"),
            )
            .where(models.VehicleMonitor.is_del == 0)
            .group_by(models.VehicleMonitor.vin_code)
            .order_by(func.count(models.VehicleMonitor.id).desc())
        )
        vin_count_dict = stmt.all()

        if not vin_count_dict:
            return []
        vin_info = [
            {
                "vin_code": record.vin_code,
                "count": record.count,
            }
            for record in vin_count_dict
            if record.count >= 2
        ]

        return vin_info
