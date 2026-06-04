from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.plugins.auth_plugin.router import get_current_user
from app.plugins.auth_plugin.models import User
from app.plugins.vehicle_plugin import schemas, services
from app.plugins.vehicle_plugin.models import VehicleStatus,VehicleGroup,TestStatus

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

# ============= 静态路由放在前面 =============

@router.get("/stats", response_model=dict)
def get_vehicle_stats(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取车辆统计信息"""
    vehicles = services.VehicleService.get_vehicles(db, limit=1000)
    return {
        "total": len(vehicles),
        "available": len([v for v in vehicles if v.vehicle_status == VehicleStatus.AVAILABLE]),
        "borrowed": len([v for v in vehicles if v.vehicle_status == VehicleStatus.BORROWED]),
        "maintenance": len([v for v in vehicles if v.vehicle_status == VehicleStatus.MAINTENANCE])
    }

# ============= 列表路由 =============
@router.get("/", response_model=List[schemas.VehicleResponse])
def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vehicle_status: Optional[VehicleStatus] = None,
    test_status: Optional[TestStatus] = None,
    vehicle_code: Optional[str] = None,
    vin_code: Optional[str] = None,
    group: Optional[VehicleGroup] = None,
    plate_number: Optional[str] = None,
    model: Optional[str] = None,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取车辆列表"""
    return services.VehicleService.get_vehicles(
        db,
        skip=skip,
        limit=limit,
        group=group,
        plate_number=plate_number,
        vehicle_status=vehicle_status,
        test_status=test_status,
        vehicle_code=vehicle_code,
        vin_code=vin_code,
        model=model
    )

@router.post("/", response_model=schemas.VehicleResponse, status_code=201)
def create_vehicle(
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """创建车辆"""
    return services.VehicleService.create_vehicle(db, vehicle)

# ============= 动态路由放在最后 =============
@router.get("/{vehicle_id}", response_model=schemas.VehicleResponse)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取单个车辆信息"""
    return services.VehicleService.get_vehicle(db, vehicle_id)

@router.put("/{vehicle_id}", response_model=schemas.VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_update: schemas.VehicleUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """更新车辆信息"""
    return services.VehicleService.update_vehicle(db, vehicle_id, vehicle_update)

@router.delete("/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """删除车辆"""
    services.VehicleService.delete_vehicle(db, vehicle_id)
    return {"message": "Vehicle deleted successfully"}

borrow_router = APIRouter(prefix="/borrows", tags=["borrows"])

# ============= 静态路由 =============
@borrow_router.get("/stats", response_model=dict)
def get_borrow_stats(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取借用统计信息"""
    records = services.BorrowService.get_borrow_records(db, limit=1000)
    return {
        "total": len(records),
        "active": len([r for r in records if r.status == "active"]),
        "returned": len([r for r in records if r.status == "returned"]),
        "cancelled": len([r for r in records if r.status == "cancelled"])
    }

# ============= 列表路由 =============
@borrow_router.get("/", response_model=List[schemas.BorrowRecordResponse])
def get_borrow_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    model: Optional[str] = None,
    vehicle_code: Optional[str] = None,
    vin_code: Optional[str] = None,
    status: Optional[str] = None,
    borrower: Optional[str] = None,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取借用记录列表"""
    return services.BorrowService.get_borrow_records(db, skip=skip, limit=limit, model=model,
                                                     vehicle_code=vehicle_code, vin_code=vin_code,
                                                     status=status, borrower=borrower
)

@borrow_router.post("/", response_model=schemas.BorrowRecordResponse, status_code=201)
def create_borrow_record(
    borrow: schemas.BorrowRecordCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """创建借用记录"""
    return services.BorrowService.create_borrow_record(db, borrow)

# ============= 动态路由 =============
@borrow_router.get("/{record_id}", response_model=schemas.BorrowRecordResponse)
def get_borrow_record(
    record_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取单个借用记录"""
    return services.BorrowService.get_borrow_record(db, record_id)

@borrow_router.post("/{record_id}/return", response_model=schemas.BorrowRecordResponse)
def return_vehicle(
    record_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """归还车辆"""
    return services.BorrowService.return_vehicle(db, record_id)

@borrow_router.post("/{record_id}/cancel", response_model=schemas.BorrowRecordResponse)
def cancel_borrow(
    record_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """取消借用"""
    return services.BorrowService.cancel_borrow(db, record_id)