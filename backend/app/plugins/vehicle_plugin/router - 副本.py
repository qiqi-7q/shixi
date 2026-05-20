from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.plugins.auth_plugin.router import get_current_user
from app.plugins.auth_plugin.models import User
from app.plugins.vehicle_plugin import schemas, services
from app.plugins.vehicle_plugin.models import VehicleStatus

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

# 车辆管理路由
@router.get("/", response_model=List[schemas.VehicleResponse])
def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[VehicleStatus] = None,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取车辆列表"""
    return services.VehicleService.get_vehicles(db, skip=skip, limit=limit, status=status)

@router.get("/{vehicle_id}", response_model=schemas.VehicleResponse)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取单个车辆信息"""
    return services.VehicleService.get_vehicle(db, vehicle_id)

@router.post("/", response_model=schemas.VehicleResponse, status_code=201)
def create_vehicle(
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """创建车辆"""
    return services.VehicleService.create_vehicle(db, vehicle)

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

# 借用记录路由
borrow_router = APIRouter(prefix="/borrows", tags=["borrows"])

@borrow_router.get("/", response_model=List[schemas.BorrowRecordResponse])
def get_borrow_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取借用记录列表"""
    return services.BorrowService.get_borrow_records(db, skip=skip, limit=limit, status=status)

@borrow_router.get("/{record_id}", response_model=schemas.BorrowRecordResponse)
def get_borrow_record(
    record_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取单个借用记录"""
    return services.BorrowService.get_borrow_record(db, record_id)

@borrow_router.post("/", response_model=schemas.BorrowRecordResponse, status_code=201)
def create_borrow_record(
    borrow: schemas.BorrowRecordCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """创建借用记录"""
    return services.BorrowService.create_borrow_record(db, borrow)

@borrow_router.post("/{record_id}/return", response_model=schemas.BorrowRecordResponse)
def return_vehicle(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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