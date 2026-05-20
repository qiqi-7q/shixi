from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from fastapi import HTTPException, status

from app.plugins.vehicle_plugin import models, schemas
from app.plugins.vehicle_plugin.models import VehicleStatus


class VehicleService:
    @staticmethod
    def get_vehicles(
            db: Session,
            skip: int = 0,
            limit: int = 100,
            status: Optional[VehicleStatus] = None,
            vehicle_code: Optional[str] = None,
            vin: Optional[str] = None,
            model: Optional[str] = None
    ) -> List[models.Vehicle]:
        query = db.query(models.Vehicle)

        if status:
            query = query.filter(models.Vehicle.status == status)
        if vehicle_code:
            query = query.filter(models.Vehicle.vehicle_code.contains(vehicle_code))
        if vin:
            query = query.filter(models.Vehicle.vin.contains(vin))
        if model:
            query = query.filter(models.Vehicle.model.contains(model))

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_vehicle(db: Session, vehicle_id: int) -> models.Vehicle:
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        return vehicle

    @staticmethod
    def get_vehicle_by_code(db: Session, vehicle_code: str) -> models.Vehicle:
        return db.query(models.Vehicle).filter(models.Vehicle.vehicle_code == vehicle_code).first()

    @staticmethod
    def create_vehicle(db: Session, vehicle: schemas.VehicleCreate) -> models.Vehicle:
        # 检查车辆编号是否已存在
        existing = VehicleService.get_vehicle_by_code(db, vehicle.vehicle_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle code already exists"
            )

        db_vehicle = models.Vehicle(**vehicle.model_dump())
        db.add(db_vehicle)
        db.commit()
        db.refresh(db_vehicle)
        return db_vehicle

    @staticmethod
    def update_vehicle(db: Session, vehicle_id: int, vehicle_update: schemas.VehicleUpdate) -> models.Vehicle:
        db_vehicle = VehicleService.get_vehicle(db, vehicle_id)

        update_data = vehicle_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vehicle, field, value)

        db.commit()
        db.refresh(db_vehicle)
        return db_vehicle

    @staticmethod
    def delete_vehicle(db: Session, vehicle_id: int):
        db_vehicle = VehicleService.get_vehicle(db, vehicle_id)
        db.delete(db_vehicle)
        db.commit()


class BorrowService:
    @staticmethod
    def get_borrow_records(
            db: Session,
            skip: int = 0,
            limit: int = 100,
            status: Optional[str] = None
    ) -> List[models.BorrowRecord]:
        query = db.query(models.BorrowRecord)
        if status:
            query = query.filter(models.BorrowRecord.status == status)
        return query.order_by(models.BorrowRecord.borrow_time.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_borrow_record(db: Session, record_id: int) -> models.BorrowRecord:
        record = db.query(models.BorrowRecord).filter(models.BorrowRecord.id == record_id).first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Borrow record not found"
            )
        return record

    @staticmethod
    def get_active_borrows_by_vehicle(db: Session, vehicle_id: int) -> List[models.BorrowRecord]:
        return db.query(models.BorrowRecord).filter(
            and_(
                models.BorrowRecord.vehicle_id == vehicle_id,
                models.BorrowRecord.status == "active"
            )
        ).all()

    @staticmethod
    def create_borrow_record(db: Session, borrow: schemas.BorrowRecordCreate) -> models.BorrowRecord:
        # 检查车辆是否存在
        vehicle = VehicleService.get_vehicle(db, borrow.vehicle_id)

        # 检查车辆状态
        if vehicle.status != VehicleStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle is not available for borrowing"
            )

        # 创建借用记录
        db_borrow = models.BorrowRecord(
            **borrow.model_dump(),
            vehicle_code=vehicle.vehicle_code,
            model=vehicle.model,
            vin=vehicle.vin,
            status="active"
        )

        # 更新车辆状态
        vehicle.status = VehicleStatus.BORROWED

        db.add(db_borrow)
        db.commit()
        db.refresh(db_borrow)
        return db_borrow

    @staticmethod
    def return_vehicle(db: Session, record_id: int) -> models.BorrowRecord:
        record = BorrowService.get_borrow_record(db, record_id)

        if record.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This borrow record is not active"
            )

        # 更新借用记录
        record.status = "returned"
        record.return_time = datetime.now()

        # 更新车辆状态
        vehicle = VehicleService.get_vehicle(db, record.vehicle_id)
        vehicle.status = VehicleStatus.AVAILABLE

        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def cancel_borrow(db: Session, record_id: int) -> models.BorrowRecord:
        record = BorrowService.get_borrow_record(db, record_id)

        if record.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This borrow record is not active"
            )

        # 更新借用记录
        record.status = "cancelled"

        # 更新车辆状态
        vehicle = VehicleService.get_vehicle(db, record.vehicle_id)
        vehicle.status = VehicleStatus.AVAILABLE

        db.commit()
        db.refresh(record)
        return record