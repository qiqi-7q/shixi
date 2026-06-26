from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.plugins.vehicle_monitor_plugin import schemas, services

router = APIRouter()


# 1. 创建单条记录
@router.post("/create")
async def create_monitor(vin_code: str, db: AsyncSession = Depends(get_db)):
    result = await services.VehicleMonitorService.create_vehicle_monitor(
        db=db, vin_code=vin_code
    )
    if result == "success":
        return {"message": "数据创建成功", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


# 2. 获取列表
@router.get("/fixsearch")
async def get_monitors(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    vin_code: Optional[str] = None,
):
    result = await services.VehicleMonitorService.get_vehicle_monitors(
        db,
        skip=skip,
        limit=limit,
        vin_code=vin_code,
    )
    return {"data": result, "message": "success", "code": 200}


# 3. 获取单条详情
@router.get("/getmonitor/{monitor_id}")
async def get_monitor(monitor_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.VehicleMonitorService.get_vehicle_monitor(
        db, monitor_id=monitor_id
    )
    if isinstance(result, str):
        return {"data": None, "message": result, "code": 400}
    return {"data": result, "message": "success", "code": 200}


# 4. 更新
@router.put("/updatemonitor/{monitor_id}")
async def update_monitor(
    monitor_id: int,
    monitor: schemas.VehicleMonitorUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await services.VehicleMonitorService.update_vehicle_monitor(
        db, monitor_id=monitor_id, monitor=monitor
    )
    if result == "success":
        return {"message": "数据更新成功", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


# 5. 删除
@router.delete("/delmonitor/{monitor_id}")
async def delete_monitor(monitor_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.VehicleMonitorService.delete_vehicle_monitor(
        db, monitor_id=monitor_id
    )
    if result == "success":
        return {"message": "数据删除成功", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}
