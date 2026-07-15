import time
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.plugins.vehicle_monitor_plugin import schemas, services

router = APIRouter()


# 3. 获取单条详情
@router.get("/getmonitor/{monitor_id}")
async def get_monitor(monitor_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.VehicleMonitorService.get_vehicle_monitor(
        db, monitor_id=monitor_id
    )
    if isinstance(result, str):
        return {"data": None, "message": result, "code": 400}
    return {"data": result, "message": "success", "code": 200}


TIME_FIELDS = {"create_time", "update_time"}


@router.post("/advsearch")
async def get_vehicle_monitors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    conditions: Optional[List[dict]] = None,
    sort_by: Optional[str] = Query(None, description="排序字段名（不提供则不排序）"),
    sort_order: Optional[str] = Query(
        "asc", description="排序方向：asc（升序，默认）/ desc（降序）"
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取车辆监控记录列表（高级查询）

    - 支持的字段：{schemas.VEHICLE_MONITOR_WHITELIST}
    - 支持的操作符：=, !=, <, <=, >, >=, icontains, between, not_between
    - between 和 not_between 的值必须是数组，且包含两个元素
    - 时间字段只支持 between/not_between 操作符
    - 时间字段的值如果是纯日期，将自动添加 00:00:00 或 23:59:59
    """

    if conditions:
        for cond in conditions:
            # 支持多种字段名格式
            field_name = (
                cond.get("advanced_field") or cond.get("field") or cond.get("column")
            )
            operator = (
                cond.get("advanced_operator") or cond.get("operator") or cond.get("op")
            )
            field_value = cond.get("advanced_value") or cond.get("value")

            if not field_name:
                return {
                    "message": "条件中缺少字段名（advanced_field/field/column）",
                    "code": 400,
                }
            if not operator:
                return {
                    "message": f"字段 {field_name} 缺少操作符（advanced_operator/operator/op）",
                    "code": 400,
                }

            # 时间字段只支持 between/not_between 操作符
            if field_name in TIME_FIELDS and operator not in ("between", "not_between"):
                return {
                    "message": f"时间字段 {field_name} 只支持 between/not_between 操作符",
                    "code": 400,
                }

            # between/not_between 的值必须是数组
            if operator in ("between", "not_between"):
                if not isinstance(field_value, list) or len(field_value) != 2:
                    return {
                        "message": f"操作符 {operator} 的值必须是包含两个元素的数组",
                        "code": 400,
                    }
                # 时间字段特殊处理：将结束日期调整为当天的 23:59:59
                if field_name in TIME_FIELDS:

                    start_value = field_value[0]
                    end_value = field_value[1]

                    # 处理开始时间：如果是纯日期，添加 00:00:00
                    if isinstance(start_value, str) and len(start_value) == 10:
                        start_value = f"{start_value} 00:00:00"

                    # 处理结束时间：如果是纯日期，添加 23:59:59
                    if isinstance(end_value, str) and len(end_value) == 10:
                        end_value = f"{end_value} 23:59:59"

                    # 更新条件中的值
                    cond["value"] = [start_value, end_value]
                    # 如果使用的是 advanced_value，也需要更新
                    if "advanced_value" in cond:
                        cond["advanced_value"] = [start_value, end_value]

            if field_name not in schemas.VEHICLE_MONITOR_WHITELIST:
                return {
                    "message": f"无效的字段: {field_name} ",
                    "code": 400,
                }
            if operator not in settings.ADVANCED_OPERATORS:
                return {
                    "message": f"无效的操作: {operator} ",
                    "code": 400,
                }

    vehicleMonitorData = await services.VehicleMonitorService.get_vehicle_monitors(
        db,
        skip=skip,
        limit=limit,
        conditions=conditions,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return {"data": vehicleMonitorData, "message": "success", "code": 200}


@router.get("/getvinlist")
async def get_vin_list(keyword:Optional[str]=None,db: AsyncSession = Depends(get_db)):
    """获取车辆vin列表"""
    result = await services.VehicleMonitorService.get_vin_list(db,keyword=keyword)
    return {"data": result, "message": "success", "code": 200}


# 获取单车用车时长、使用率、行驶里程、行驶轨迹
@router.get("/carinfo/{vin_code}")
async def get_cars_info(
    vin_code: str,
    db: AsyncSession = Depends(get_db),
):
    """获取单车车辆用车时长、使用率、行驶里程，随时间变化"""
    result = await services.VehicleMonitorService.get_cars_info(
        db,
        vin_code=vin_code,
    )

    return {"data": result, "message": "success", "code": 200}


@router.get("/getgroups")
async def get_groups(
    db: AsyncSession = Depends(get_db),
    model: Optional[str] = None,
):
    """按车型、组别获取使用率，随时间变化"""
    result = await services.VehicleMonitorService.get_groups(
        db,
        model=model,
    )
    return {"data": result, "message": "success", "code": 200}


@router.get("/getusages")
async def get_usages(
    models: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
):
    """选定多车型、时间范围，根据VIN统计单车的平均使用率"""
    result = await services.VehicleMonitorService.get_usages(
        db, models, start_date, end_date
    )
    return {"data": result, "message": "success", "code": 200}


@router.get("/getdistences")
async def get_distences(
    models: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
):
    """选定多车型、时间范围，根据VIN统计单车的平均行驶里程"""
    result = await services.VehicleMonitorService.get_distences(
        db, models, start_date, end_date
    )
    return {"data": result, "message": "success", "code": 200}


@router.get("/getvin")
async def get_vin(db: AsyncSession = Depends(get_db)):
    """获取出现次数大于等于2次的VIN码列表"""
    result = await services.VehicleMonitorService.get_vin(db)
    return {"data": result, "message": "success", "code": 200}
