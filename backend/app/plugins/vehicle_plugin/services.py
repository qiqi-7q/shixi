from typing import Any, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.plugins.vehicle_plugin import models, schemas

ADVANCED_OPERATORS = {
    "eq": lambda field, value: field == value,  # 等于
    "ne": lambda field, value: field != value,  # 不等于
    "contains": lambda field, value: field.contains(value),  # 包含
    "icontains": lambda field, value: field.ilike(f"%{value}%"),  # 忽略大小写包含
    "gt": lambda field, value: field > value,  # 大于
    "gte": lambda field, value: field >= value,  # 大于等于
    "lt": lambda field, value: field < value,  # 小于
    "lte": lambda field, value: field <= value,  # 小于等于
}


class VehicleService:

    @staticmethod
    def _build_condition(field_name: str, operator: str, value: Any):
        # 构建查询条件
        field = getattr(models.Vehicle, field_name)
        op_func = ADVANCED_OPERATORS.get(operator, ADVANCED_OPERATORS["eq"])
        return op_func(field, value)

    @staticmethod
    def get_vehicles(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        conditions: Optional[List[dict]] = None,
    ) -> List[models.Vehicle]:
        query = db.query(models.Vehicle)

        get_condition = []

        for cond in conditions:
            field_name = cond["advanced_field"]
            operator = cond["advanced_operator"]
            value = cond["advanced_value"]

            condition = VehicleService._build_condition(field_name, operator, value)
            if condition is not None:
                get_condition.append(condition)

        query = query.filter(and_(*get_condition))

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_vehicles_simple(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        vehicle_status: Optional[models.VehicleStatus] = None,
        group: Optional[models.VehicleGroup] = None,
        vin_code: Optional[str] = None,
        model: Optional[str] = None,
    ) -> List[models.Vehicle]:

        query = db.query(models.Vehicle)

        if vehicle_status:
            query = query.filter(models.Vehicle.vehicle_status == vehicle_status)
        if group:
            query = query.filter(models.Vehicle.group == group)
        if vin_code:
            query = query.filter(models.Vehicle.vin_code.contains(vin_code))
        if model:
            query = query.filter(models.Vehicle.model == model)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_vehicle(db: Session, vehicle_id: int) -> models.Vehicle:
        vehicle = (
            db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
        )
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
            )
        return vehicle

    @staticmethod
    def get_vehicle_status(db: Session, vehicle_id: int) -> dict:
        vehicle = VehicleService.get_vehicle(db, vehicle_id)
        if vehicle.vehicle_status == models.VehicleStatus.AVAILABLE:
            return {"now_status": "Available"}
        else:
            return {"now_status": "Already Borrowed"}

    @staticmethod
    def get_vehicle_by_code(db: Session, vehicle_code: str) -> models.Vehicle:
        return (
            db.query(models.Vehicle)
            .filter(models.Vehicle.vehicle_code == vehicle_code)
            .first()
        )

    @staticmethod
    def create_vehicle(db: Session, vehicle: schemas.VehicleCreate) -> models.Vehicle:
        # 检查车辆编号是否已存在
        existing = VehicleService.get_vehicle_by_code(db, vehicle.vehicle_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle code already exists",
            )

        db_vehicle = models.Vehicle(**vehicle.model_dump())
        db.add(db_vehicle)
        db.commit()
        db.refresh(db_vehicle)
        return db_vehicle

    @staticmethod
    def update_vehicle(
        db: Session, vehicle_id: int, vehicle_update: schemas.VehicleUpdate
    ) -> models.Vehicle:
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
    def _build_condition(field_name: str, operator: str, value: Any):
        # 构建查询条件
        field = getattr(models.BorrowRecord, field_name)
        op_func = ADVANCED_OPERATORS.get(operator, ADVANCED_OPERATORS["eq"])
        return op_func(field, value)

    @staticmethod
    def get_borrow_records_simple(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        model: Optional[str] = None,
        vin_code: Optional[str] = None,
        borrow_status: Optional[str] = None,
    ) -> List[models.BorrowRecord]:
        query = db.query(models.BorrowRecord)
        if borrow_status:
            query = query.filter(models.BorrowRecord.borrow_status == borrow_status)
        if model:
            query = query.filter(models.BorrowRecord.model == model)
        if vin_code:
            query = query.filter(models.BorrowRecord.vin_code.contains(vin_code))

        return (
            query.order_by(models.BorrowRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_borrow_records(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        conditions: Optional[List[dict]] = None,
    ) -> List[models.BorrowRecord]:
        query = db.query(models.BorrowRecord)

        borrow_condition = []

        for cond in conditions:
            field_name = cond["advanced_field"]
            operator = cond["advanced_operator"]
            value = cond["advanced_value"]

            condition = BorrowService._build_condition(field_name, operator, value)
            if condition is not None:
                borrow_condition.append(condition)

        query = query.filter(and_(*borrow_condition))

        return (
            query.order_by(models.BorrowRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_borrow_record(db: Session, record_id: int) -> models.BorrowRecord:
        record = (
            db.query(models.BorrowRecord)
            .filter(models.BorrowRecord.id == record_id)
            .first()
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Borrow record not found"
            )
        return record

    @staticmethod
    def get_active_borrows_by_vehicle(
        db: Session, vehicle_id: int
    ) -> List[models.BorrowRecord]:
        return (
            db.query(models.BorrowRecord)
            .filter(
                and_(
                    models.BorrowRecord.vehicle_id == vehicle_id,
                    models.BorrowRecord.borrow_status == "active",
                )
            )
            .all()
        )

    @staticmethod
    def create_borrow_record(
        db: Session, borrow: schemas.BorrowRecordCreate
    ) -> models.BorrowRecord:
        # 检查车辆是否存在
        vehicle = VehicleService.get_vehicle(db, borrow.vehicle_id)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
            )
        # 检查车辆状态
        if vehicle.vehicle_status != models.VehicleStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle is not available for borrowing",
            )

        # 创建借用记录
        db_borrow = models.BorrowRecord(**borrow.model_dump())

        # 更新车辆状态
        vehicle.vehicle_status = models.VehicleStatus.BORROWED

        db.add(db_borrow)
        db.commit()
        db.refresh(db_borrow)
        return db_borrow

    @staticmethod
    def return_vehicle(db: Session, record_id: int) -> models.BorrowRecord:
        record = BorrowService.get_borrow_record(db, record_id)

        if record.borrow_status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This borrow record is not active",
            )

        # 更新借用记录
        record.borrow_status = "returned"

        # 更新车辆状态
        vehicle = VehicleService.get_vehicle(db, record.vehicle_id)
        vehicle.vehicle_status = models.VehicleStatus.AVAILABLE

        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def cancel_borrow(db: Session, record_id: int) -> models.BorrowRecord:
        record = BorrowService.get_borrow_record(db, record_id)

        if record.borrow_status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This borrow record is not active",
            )

        # 更新借用记录
        record.borrow_status = "cancelled"

        # 更新车辆状态
        vehicle = VehicleService.get_vehicle(db, record.vehicle_id)
        vehicle.vehicle_status = models.VehicleStatus.AVAILABLE

        db.commit()
        db.refresh(record)
        return record
