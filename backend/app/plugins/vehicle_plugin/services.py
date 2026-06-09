from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.plugins.vehicle_plugin import models, schemas
from app.utils.build_condition import build_condition


class VehicleService:

    @staticmethod
    async def get_vehicles(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        conditions: Optional[List[dict]] = None,
    ) -> List[models.Vehicle]:
        stmt = select(models.Vehicle)
        if conditions:
            get_condition = []

            for cond in conditions:
                field_name = cond["advanced_field"]
                operator = cond["advanced_operator"]
                value = cond["advanced_value"]

                condition = build_condition(models.Vehicle, field_name, operator, value)
                if condition is not None:
                    get_condition.append(condition)
            # 应用查询条件
            stmt = stmt.where(and_(*get_condition))
        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_vehicles_simple(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        vehicle_status: Optional[models.VehicleStatus] = None,
        group: Optional[models.VehicleGroup] = None,
        vin_code: Optional[str] = None,
        model: Optional[str] = None,
    ) -> List[models.Vehicle]:
        stmt = select(models.Vehicle)

        if vehicle_status:
            stmt = stmt.where(models.Vehicle.vehicle_status == vehicle_status)
        if group:
            stmt = stmt.where(models.Vehicle.group == group)
        if vin_code:
            stmt = stmt.where(models.Vehicle.vin_code.contains(vin_code))
        if model:
            stmt = stmt.where(models.Vehicle.model == model)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_vehicle(db: AsyncSession, vehicle_id: int) -> models.Vehicle | str:
        vehicle = await db.get(models.Vehicle, vehicle_id)
        if not vehicle:
            return "Vehicle not found"
        return vehicle

    @staticmethod
    async def get_vehicle_status(db: AsyncSession, vehicle_id: int) -> str:
        vehicle = await VehicleService.get_vehicle(db, vehicle_id)
        if vehicle.vehicle_status == models.VehicleStatus.AVAILABLE:
            return "Available"
        else:
            return "Already Borrowed"

    @staticmethod
    async def vehicle_check(db: AsyncSession, vehicles) -> str | None:
        if not vehicles:
            return "Vehicle data is missing"
        if not vehicles.vehicle_code:
            return "Vehicle code is missing"
        if not vehicles.vin_code:
            return "VIN code is missing"
        if not vehicles.model:
            return "Model is missing"
        if not vehicles.owner_name:
            return "Owner name is missing"
        if not vehicles.plate_number:
            return "Plate number is missing"
        if not vehicles.editor:
            return "Editor is missing"
        vecodeExisting = await db.execute(
            select(models.Vehicle).where(
                models.Vehicle.vehicle_code == vehicles.vehicle_code
            )
        )
        if vecodeExisting.scalars().first():
            return "vehicle_code already exists"
        vinExisting = await db.execute(
            select(models.Vehicle).where(models.Vehicle.vin_code == vehicles.vin_code)
        )
        if vinExisting.scalars().first():
            return "vin_code already exists"

    @staticmethod
    async def create_vehicle(
        db: AsyncSession, vehicle: schemas.VehicleCreate
    ) -> models.Vehicle | str:
        check_result = await VehicleService.vehicle_check(db, vehicle)
        if check_result:
            return check_result

        db_vehicle = models.Vehicle(**vehicle.model_dump())
        db.add(db_vehicle)
        await db.commit()
        await db.refresh(db_vehicle)
        return "success"

    @staticmethod
    async def update_vehicle(
        db: AsyncSession, vehicle_id: int, vehicle_update: schemas.VehicleUpdate
    ) -> str:
        db_vehicle = await VehicleService.get_vehicle(db, vehicle_id)
        if not db_vehicle:
            return "Vehicle not found"
        check_result = await VehicleService.vehicle_check(db, vehicle_update)
        if check_result:
            return check_result
        update_data = vehicle_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vehicle, field, value)
        await db.commit()
        await db.refresh(db_vehicle)
        return "success"

    @staticmethod
    async def delete_vehicle(db: AsyncSession, vehicle_id: int) -> str:
        db_vehicle = await VehicleService.get_vehicle(db, vehicle_id)
        if not db_vehicle:
            return "Vehicle not found"
        await db.delete(db_vehicle)
        await db.commit()
        return "success"


class BorrowService:

    # @staticmethod
    # def _build_condition(field_name: str, operator: str, value: Any):
    #     # 构建查询条件
    #     field = getattr(models.BorrowRecord, field_name)
    #     op_func = settings.ADVANCED_OPERATORS.get(operator, settings.ADVANCED_OPERATORS["eq"])
    #     return op_func(field, value)

    @staticmethod
    async def get_borrow_records_simple(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        model: Optional[str] = None,
        vin_code: Optional[str] = None,
        borrow_status: Optional[str] = None,
    ) -> List[models.BorrowRecord]:
        stmt = select(models.BorrowRecord)
        if borrow_status:
            stmt = stmt.where(models.BorrowRecord.borrow_status == borrow_status)
        if model:
            stmt = stmt.where(models.BorrowRecord.model == model)
        if vin_code:
            stmt = stmt.where(models.BorrowRecord.vin_code.contains(vin_code))
        stmt = stmt.order_by(models.BorrowRecord.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_borrow_records(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        conditions: Optional[List[dict]] = None,
    ) -> List[models.BorrowRecord]:
        stmt = select(models.BorrowRecord)
        if conditions:
            borrow_condition = []

            for cond in conditions:
                field_name = cond["advanced_field"]
                operator = cond["advanced_operator"]
                value = cond["advanced_value"]

                condition = build_condition(
                    models.BorrowRecord, field_name, operator, value
                )
                if condition is not None:
                    borrow_condition.append(condition)

            stmt = stmt.where(and_(*borrow_condition))
        stmt = stmt.order_by(models.BorrowRecord.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_borrow_record(
        db: AsyncSession, record_id: int
    ) -> models.BorrowRecord | str:
        record = await db.get(models.BorrowRecord, record_id)

        if not record:
            return "Borrow record not found"
        return record

    # 获取车辆的所有活动借用记录
    @staticmethod
    async def get_active_borrows_by_vehicle(
        db: AsyncSession, vehicle_id: int
    ) -> List[models.BorrowRecord]:
        stmt = select(models.BorrowRecord).where(
            and_(
                models.BorrowRecord.vehicle_id == vehicle_id,
                models.BorrowRecord.borrow_status == "active",
            )
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_borrow_record(
        db: AsyncSession, borrow: schemas.BorrowRecordCreate
    ) -> bool | str:
        if not borrow.borrower:
            return "Borrower is missing"
        if not borrow.borrow_time:
            return "Borrow time is missing"
        # 检查车辆是否存在
        vehicle = await VehicleService.get_vehicle(db, borrow.vehicle_id)
        if not vehicle:
            return "Vehicle not found"

        # 创建借用记录
        db_borrow = models.BorrowRecord(**borrow.model_dump())

        # 更新车辆状态
        vehicle.vehicle_status = models.VehicleStatus.BORROWED

        db.add(db_borrow)
        await db.commit()
        await db.refresh(db_borrow)
        return "success"

    @staticmethod
    async def update_borrow_record(
        db: AsyncSession, record_id: int, borrow_update: schemas.BorrowRecordUpdate
    ) -> bool | str:
        if not borrow_update.borrower:
            return "Borrower is missing"
        if not borrow_update.borrow_time:
            return "Borrow time is missing"
        record = await BorrowService.get_borrow_record(db, record_id)
        if not record:
            return "Borrow record not found"
        update_data = borrow_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)

        await db.commit()
        await db.refresh(record)
        return "success"

    @staticmethod
    async def delete_borrow_record(db: AsyncSession, record_id: int):
        record = await BorrowService.get_borrow_record(db, record_id)
        if not record:
            return "Borrow record not found"
        await db.delete(record)
        await db.commit()
        return "success"

    @staticmethod
    async def return_vehicle(db: AsyncSession, record_id: int) -> bool | str:
        record = await BorrowService.get_borrow_record(db, record_id)
        if not record:
            return "Borrow record not found"
        if not record.borrow_status != "active":
            return "This borrow record is not active for returning"

        # 更新借用记录
        record.borrow_status = "returned"

        # 更新车辆状态
        vehicle = await VehicleService.get_vehicle(db, record.vehicle_id)
        vehicle.vehicle_status = models.VehicleStatus.AVAILABLE

        await db.commit()
        await db.refresh(record)
        return "success"

    @staticmethod
    async def cancel_borrow(db: AsyncSession, record_id: int) -> bool | str:
        record = await BorrowService.get_borrow_record(db, record_id)

        if not record:
            return "Borrow record not found"
        if not record.borrow_status != "active":
            return "This borrow record is not active for canceling"

        # 更新借用记录
        record.borrow_status = "cancelled"

        # 更新车辆状态
        vehicle = await VehicleService.get_vehicle(db, record.vehicle_id)
        vehicle.vehicle_status = models.VehicleStatus.AVAILABLE

        await db.commit()
        await db.refresh(record)
        return "success"
