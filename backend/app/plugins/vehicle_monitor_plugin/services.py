from datetime import date
from typing import List, Optional

# from app.utils.leapcloud_data import (
#     get_vehicle_status,
#     get_fire_states,
#     get_charge_states,
# )
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from app.plugins.vehicle_monitor_plugin import models, schemas
from app.utils.build_condition import build_condition


class VehicleMonitorService:

    # @staticmethod
    # async def get_vehicle_monitors(
    #     db: AsyncSession,
    #     skip: int = 0,
    #     limit: int = 100,
    #     vin_code: Optional[str] = None,
    #     model: Optional[str] = None,
    #     start_date: Optional[date] = None,
    #     end_date: Optional[date] = None,
    # ):
    #     filters = [
    #         models.VehicleMonitor.is_del == 0,
    #     ]
    #     if vin_code:
    #         filters.append(models.VehicleMonitor.vin_code.icontains(vin_code))
    #     if model:
    #         filters.append(models.VehicleMonitor.model.icontains(model))
    #     if start_date:
    #         filters.append(models.VehicleMonitor.monitor_date >= start_date)
    #     if end_date:
    #         filters.append(models.VehicleMonitor.monitor_date <= end_date)
    #
    #     # 2. 先查符合条件的总条数（不带分页）
    #     count_stmt = select(func.count(models.VehicleMonitor.id)).where(*filters)
    #     total = await db.scalar(count_stmt) or 0
    #
    #     # 3. 再查分页数据
    #     data_stmt = (
    #         select(models.VehicleMonitor)
    #         .where(*filters)
    #         .order_by(models.VehicleMonitor.monitor_date.desc())
    #         .offset(skip)
    #         .limit(limit)
    #     )
    #     result = await db.execute(data_stmt)
    #     data_list = list(result.scalars().all())
    #
    #     return {"items": data_list, "total": total, "skip": skip, "limit": limit}

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

        # 分页查询
        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        return {
            "items": list(result.scalars().all()),
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    async def get_vin_list(
        db: AsyncSession,
    ):
        stmt = await db.execute(
            select(models.VehicleMonitor.vin_code).where(
                models.VehicleMonitor.is_del == 0,
            )
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

        car_info_dict = stmt.mappings().all()

        if not car_info_dict:
            return []
        car_info = [
            {
                "vin_code": record["vin_code"],
                "power_duration": record["power_duration"],
                "usage": record["usage"],
                "distance": record["distance"],
                "monitor_date": record["monitor_date"],
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
        rows = result.mappings().all()

        groups = []
        for row in rows:
            groups.append(
                {
                    "group": row["group"],
                    "monitor_date": row["monitor_date"],
                    "avg_usage": round(float(row["avg_usage"]), 2),
                    "count": row["count"],
                }
            )

        return groups

    @staticmethod
    async def get_usages(db: AsyncSession, monitor_date: date) -> list[dict]:
        stmt = await db.execute(
            select(
                models.VehicleMonitor.id,
                models.VehicleMonitor.vin_code,
                models.VehicleMonitor.power_duration,
                models.VehicleMonitor.usage,
            )
            .where(
                models.VehicleMonitor.is_del == 0,
                models.VehicleMonitor.monitor_date == monitor_date,
            )
            .order_by(models.VehicleMonitor.usage.desc())
        )
        usages_dict = stmt.mappings().all()

        if not usages_dict:
            return []
        usage_info = [
            {
                "id": record["id"],
                "vin_code": record["vin_code"],
                "power_duration": record["power_duration"],
                "usage": record["usage"],
            }
            for record in usages_dict
        ]

        return usage_info

    @staticmethod
    async def get_distences(db: AsyncSession, monitor_date: date) -> list[dict]:
        stmt = await db.execute(
            select(
                models.VehicleMonitor.id,
                models.VehicleMonitor.vin_code,
                models.VehicleMonitor.distance,
            )
            .where(
                models.VehicleMonitor.is_del == 0,
                models.VehicleMonitor.monitor_date == monitor_date,
            )
            .order_by(models.VehicleMonitor.distance.desc())
        )
        distances_dict = stmt.mappings().all()

        if not distances_dict:
            return []
        distances_info = [
            {
                "id": record["id"],
                "vin_code": record["vin_code"],
                "distance": record["distance"],
            }
            for record in distances_dict
        ]

        return distances_info
