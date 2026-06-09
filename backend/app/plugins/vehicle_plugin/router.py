from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.plugins.vehicle_plugin import models, schemas, services

router = APIRouter()


# ============= 静态路由放在前面 =============


@router.get("/stats")
async def get_vehicle_stats(
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取车辆统计信息"""
    vehicles = await services.VehicleService.get_vehicles(db, limit=1000)
    stats = {
        "total": len(vehicles),
        "available": len(
            [v for v in vehicles if v.vehicle_status == models.VehicleStatus.AVAILABLE]
        ),
        "borrowed": len(
            [v for v in vehicles if v.vehicle_status == models.VehicleStatus.BORROWED]
        ),
        "maintenance": len(
            [
                v
                for v in vehicles
                if v.vehicle_status == models.VehicleStatus.MAINTENANCE
            ]
        ),
    }
    return {
        "data": stats,
        "message": "success",
        "code": 200,
    }


# ============= 列表路由 =============
@router.post("/advsearch")
async def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    conditions: Optional[List[dict]] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取车辆列表（高级查询）"""

    if not conditions:
        return {"message": "Invalid advanced conditions", "code": 400}

    for cond in conditions:
        if cond["advanced_field"] not in schemas.VEHICLE_WHITELIST:
            return {
                "message": f"Invalid advanced_field: {cond['advanced_field']} ",
                "code": 400,
            }
        if cond["advanced_operator"] not in settings.ADVANCED_OPERATORS:
            return {
                "message": f"Invalid advanced_operator: {cond['advanced_operator']} ",
                "code": 400,
            }

    vehicleData = await services.VehicleService.get_vehicles(
        db,
        skip=skip,
        limit=limit,
        conditions=conditions,
    )
    return {"data": vehicleData, "message": "success", "code": 200}


@router.get("/fixsearch")
async def get_vehicles_simple(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vehicle_status: Optional[models.VehicleStatus] = None,
    vin_code: Optional[str] = None,
    group: Optional[models.VehicleGroup] = None,
    model: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取车辆列表（固定字段查询）"""
    vehicleData = await services.VehicleService.get_vehicles_simple(
        db,
        skip=skip,
        limit=limit,
        group=group,
        vehicle_status=vehicle_status,
        vin_code=vin_code,
        model=model,
    )
    return {"data": vehicleData, "message": "success", "code": 200}


@router.post("/createvehicle")
async def create_vehicle(
    vehicle: schemas.VehicleCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """创建车辆"""
    result = await services.VehicleService.create_vehicle(db, vehicle)
    if result == "success":
        return {"message": "Vehicle created successfully", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


# ============= 动态路由放在最后 =============
@router.get("/getstatus/{vehicle_id}")
async def get_vehicle_status(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取车辆状态"""
    status = await services.VehicleService.get_vehicle_status(db, vehicle_id)
    return {"data": status, "message": "success", "code": 200}


@router.get("/getvehicle/{vehicle_id}")
async def get_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取单个车辆信息"""
    vehicleInfo = await services.VehicleService.get_vehicle(db, vehicle_id)
    if isinstance(vehicleInfo, str):
        return {"message": vehicleInfo, "code": 400, "data": None}
    return {"data": vehicleInfo, "message": "success", "code": 200}


@router.put("/updatevehicle/{vehicle_id}")
async def update_vehicle(
    vehicle_id: int,
    vehicle_update: schemas.VehicleUpdate,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """更新车辆信息"""
    result = await services.VehicleService.update_vehicle(
        db, vehicle_id, vehicle_update
    )
    if result == "success":
        return {"message": "Vehicle updated successfully", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


@router.delete("/delvehicle/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """删除车辆"""
    result = await services.VehicleService.delete_vehicle(db, vehicle_id)
    if result == "success":
        return {"message": "Vehicle deleted successfully", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


borrow_router = APIRouter()


# ============= 静态路由 =============
@borrow_router.get("/stats")
async def get_borrow_stats(
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取借用统计信息"""
    records = await services.BorrowService.get_borrow_records(db, limit=1000)
    stats = {
        "total": len(records),
        "active": len([r for r in records if r.borrow_status == "active"]),
        "returned": len([r for r in records if r.borrow_status == "returned"]),
        "cancelled": len([r for r in records if r.borrow_status == "cancelled"]),
    }
    return {"data": stats, "message": "success", "code": 200}


# ============= 列表路由 =============
@borrow_router.get("/fixsearch")
async def get_borrow_records_simple(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    model: Optional[str] = None,
    vin_code: Optional[str] = None,
    borrow_status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取借用记录列表"""
    records = await services.BorrowService.get_borrow_records_simple(
        db,
        skip=skip,
        limit=limit,
        model=model,
        vin_code=vin_code,
        borrow_status=borrow_status,
    )
    return {"data": records, "message": "success", "code": 200}


@borrow_router.post("/advsearch")
async def get_borrow_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    conditions: Optional[List[dict]] = None,
    db: AsyncSession = Depends(get_db),
):

    if not conditions:
        return {"message": "Invalid advanced conditions", "code": 400, "data": None}

    for cond in conditions:
        if cond["advanced_field"] not in schemas.BORROW_WHITELIST:
            return {
                "message": f"Invalid advanced_field: {cond['advanced_field']} ",
                "code": 400,
                "data": None,
            }
        if cond["advanced_operator"] not in settings.ADVANCED_OPERATORS:
            return {
                "message": f"Invalid advanced_operator: {cond['advanced_operator']} ",
                "code": 400,
                "data": None,
            }

    records = await services.BorrowService.get_borrow_records(
        db,
        skip=skip,
        limit=limit,
        conditions=conditions,
    )
    return {"data": records, "message": "success", "code": 200}


@borrow_router.post("/createborrow")
async def create_borrow_record(
    borrow: schemas.BorrowRecordCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """创建借用记录"""
    result = await services.BorrowService.create_borrow_record(db, borrow)
    if result == "success":
        return {
            "message": "Borrow record created successfully",
            "code": 200,
            "data": None,
        }
    else:
        return {"message": result, "code": 400, "data": None}


# ============= 动态路由 =============
@borrow_router.get("/getborrow/{record_id}")
async def get_borrow_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取单个借用记录"""
    record = await services.BorrowService.get_borrow_record(db, record_id)
    if isinstance(record, str):
        return {"message": record, "code": 400, "data": None}
    return {"data": record, "message": "success", "code": 200}


@borrow_router.put("/updateborrow/{record_id}")
async def update_borrow_record(
    record_id: int,
    borrow_update: schemas.BorrowRecordUpdate,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """更新借用记录"""
    result = await services.BorrowService.update_borrow_record(
        db, record_id, borrow_update
    )
    if result == "success":
        return {
            "message": "Borrow record updated successfully",
            "code": 200,
            "data": None,
        }
    else:
        return {"message": result, "code": 400, "data": None}


@borrow_router.delete("/delborrow/{record_id}")
async def delete_borrow_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """删除借用记录"""
    result = await services.BorrowService.delete_borrow_record(db, record_id)
    if result == "success":
        return {
            "message": "Borrow record deleted successfully",
            "code": 200,
            "data": None,
        }
    else:
        return {"message": result, "code": 400, "data": None}


@borrow_router.post("/returnvehicle/{record_id}")
async def return_vehicle(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """归还车辆"""
    result = await services.BorrowService.return_vehicle(db, record_id)
    if result == "success":
        return {"message": "Vehicle returned successfully", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


@borrow_router.post("/cancelborrow/{record_id}")
async def cancel_borrow(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """取消借用"""
    result = await services.BorrowService.cancel_borrow(db, record_id)
    if result == "success":
        return {
            "message": "Borrow record canceled successfully",
            "code": 200,
            "data": None,
        }
    else:
        return {"message": result, "code": 400, "data": None}
