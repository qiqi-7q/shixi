from io import BytesIO
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime

from fastapi import UploadFile
from openpyxl import load_workbook
from sqlalchemy import and_, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.plugins.vehicle_plugin import models, schemas

from app.utils.build_condition import build_condition, _find_enum_by_value

from sqlalchemy import func

from app.utils.handle_excel_testrecord import (
    build_enum_lookup,
    generate_unique_key,
    handle_excel_from_bytes,
)

# ============================================================
# Excel 中文表头 → Pydantic 英文字段名映射
# ============================================================
EXCEL_FIELD_MAPPING: Dict[str, str] = {
    "车型": "model",
    "组别": "group",
    "车辆阶段": "vehicle_stage",
    "车辆配置": "configuration",
    "车主权限": "owner_name",
    "车辆编号": "vehicle_code",
    "停车地点": "parking_location",
    "使用状态": "vehicle_status",
    "车辆状态": "test_status",
    "备注": "remarks",
    "VIN码": "vin_code",
    "驱动电机号/发动机号": "engine_num",
    "车牌号": "plate_number",
    "临牌到期时间": "temp_plate_expire_date",
    "临牌已办次数": "temp_plate_count",
}

# 重复判定字段（vin_code + vehicle_code 组合唯一）
REPEAT_VEHICLE_FIELDS = ["vin_code"]

# 需要强制转为字符串的字段（Excel 中纯数字列会被 openpyxl 读取为 int/float）
STRING_FIELDS = (
    "model",
    "vehicle_code",
    "vin_code",
    "owner_name",
    "plate_number",
    "vehicle_stage",
    "configuration",
    "parking_location",
    "engine_num",
    "remarks",
)


class VehicleService:

    @staticmethod
    async def get_vehicles(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        conditions: Optional[List[dict]] = None,
    ) -> dict:
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
    async def get_vehicles_simple(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        vehicle_status: Optional[str] = None,
        test_status: Optional[str] = None,
        group: Optional[str] = None,
        vin_code: Optional[str] = None,
        model: Optional[str] = None,
        driver_name: Optional[str] = None,
    ) -> dict:
        # 1. 统一收集筛选条件
        filters = []

        # 处理 vehicle_status（支持英文枚举名和中文值）
        if vehicle_status:
            filters.append(models.Vehicle.vehicle_status == vehicle_status)
        if group:
            filters.append(models.Vehicle.group == group)
        if vin_code:
            filters.append(models.Vehicle.vin_code.contains(vin_code))
        if model:
            filters.append(models.Vehicle.model == model)
        if test_status:
            filters.append(models.Vehicle.test_status == test_status)

        # 2. 先查符合条件的总条数（不带分页）
        count_stmt = select(func.count(models.Vehicle.id)).where(*filters)
        total = await db.scalar(count_stmt) or 0

        # 3. 再查分页数据
        data_stmt = (
            select(models.Vehicle)
            .where(*filters)
            .offset(skip)
            .limit(limit)
            .order_by(models.Vehicle.id.desc())
        )
        result = await db.execute(data_stmt)
        data_list = list(result.scalars().all())

        return {"items": data_list, "total": total, "skip": skip, "limit": limit}

    @staticmethod
    async def get_vehicle(db: AsyncSession, vehicle_id: int) -> models.Vehicle | str:
        vehicle = await db.get(models.Vehicle, vehicle_id)
        if not vehicle:
            return "车辆信息不存在"
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
            return "车辆数据不能为空"
        if not vehicles.vehicle_code:
            return "车辆编号不能为空"
        if not vehicles.vin_code:
            return "车辆vin码不能为空"
        if not vehicles.model:
            return "车型不能为空"
        if not vehicles.owner_name:
            return "车主权限不能为空"
        if not vehicles.plate_number:
            return "车牌号不能为空"
        vecodeExisting = await db.execute(
            select(models.Vehicle).where(
                models.Vehicle.vehicle_code == vehicles.vehicle_code
            )
        )
        if vecodeExisting.scalars().first():
            return "车辆编号已存在"
        vinExisting = await db.execute(
            select(models.Vehicle).where(models.Vehicle.vin_code == vehicles.vin_code)
        )
        if vinExisting.scalars().first():
            return "vin码已存在"

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
            return "车辆信息不存在"
        update_data = vehicle_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vehicle, field, value)
        await db.commit()
        await db.refresh(db_vehicle)
        return "success"

    @staticmethod
    async def delete_vehicle(db: AsyncSession, vehicle_id: int) -> str:
        await db.execute(
            delete(models.BorrowRecord).where(
                models.BorrowRecord.vehicle_id == vehicle_id
            )
        )
        db_vehicle = await VehicleService.get_vehicle(db, vehicle_id)
        if not db_vehicle:
            return "车辆信息不存在"
        await db.delete(db_vehicle)
        await db.commit()
        return "success"

    # ============================================================
    # 工具函数
    # ============================================================
    @staticmethod
    def _transform_record(record: dict) -> Optional[dict]:
        transformed = {}
        VEHICLE_STATUS_LOOKUP = build_enum_lookup(models.VehicleStatus)
        VEHICLE_GROUP_LOOKUP = build_enum_lookup(models.VehicleGroup)
        TEST_STATUS_LOOKUP = build_enum_lookup(models.TestStatus)

        ENUM_FIELD_LOOKUPS = {
            "vehicle_status": VEHICLE_STATUS_LOOKUP,
            "group": VEHICLE_GROUP_LOOKUP,
            "test_status": TEST_STATUS_LOOKUP,
        }

        for cn_key, en_key in EXCEL_FIELD_MAPPING.items():
            if cn_key in record:
                transformed[en_key] = record[cn_key]

        # 空值归一化：除 vin_code 外，空字符串统一转为 None
        for key in list(transformed.keys()):
            if key != "vin_code":
                val = transformed[key]
                if isinstance(val, str) and not val.strip():
                    transformed[key] = None

        for field in STRING_FIELDS:
            if field in transformed and transformed[field] is not None:
                if not isinstance(transformed[field], str):
                    transformed[field] = str(transformed[field])
                transformed[field] = transformed[field].strip()

        for enum_field, lookup in ENUM_FIELD_LOOKUPS.items():
            if enum_field in transformed and transformed[enum_field] is not None:
                raw = str(transformed[enum_field]).strip().upper()
                if raw in lookup:
                    transformed[enum_field] = lookup[raw]

        # 日期字段归一化：Excel 可能输出 datetime 对象或 2026/11/12 格式的字符串，可以为空；
        # 如果输入2026/11/12，将转换为 2026-11-12；如果输入2026-11-12，就保留
        if "temp_plate_expire_date" in transformed:
            raw_date = transformed["temp_plate_expire_date"]
            if raw_date is None:
                transformed["temp_plate_expire_date"] = None
            elif isinstance(raw_date, datetime):
                transformed["temp_plate_expire_date"] = raw_date.strftime("%Y-%m-%d")
            elif isinstance(raw_date, str):
                stripped = raw_date.strip()
                if stripped and "/" in stripped:
                    transformed["temp_plate_expire_date"] = stripped.replace("/", "-")
                elif stripped and "-" in stripped:
                    transformed["temp_plate_expire_date"] = stripped
                try:
                    parts = transformed["temp_plate_expire_date"].split("-")
                    if len(parts) == 3:
                        transformed["temp_plate_expire_date"] = (
                            f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"
                        )
                    else:
                        transformed["temp_plate_expire_date"] = None
                except (ValueError, TypeError):
                    transformed["temp_plate_expire_date"] = None
            else:
                transformed["temp_plate_expire_date"] = None

        return transformed

    # ============================================================
    # 核心入口：处理上传的车辆 Excel 文件并存入数据库
    # ============================================================
    @staticmethod
    async def process_vehicle_excel_upload(
        file: UploadFile, db: AsyncSession
    ) -> dict | str:
        # 1. 校验上传
        if file is None:
            return {"code": 400, "message": "文件上传失败：未接收到文件", "data": None}
        if not file.filename:
            return {"code": 400, "message": "文件上传失败：文件名为空", "data": None}

        filename_lower = file.filename.lower()
        if not (filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls")):
            return {
                "code": 400,
                "message": "文件上传失败：仅支持 .xlsx 或 .xls 格式",
                "data": None,
            }

        # 2. 从内存读取Excel文件内容
        content = await file.read()

        try:
            # 读取Excel文件：自动过滤全空行
            try:
                excel_records, headers = handle_excel_from_bytes(content)
                total_excel_rows = len(excel_records)
            except Exception as e:
                return {
                    "message": f"Excel数据处理失败：{str(e)}",
                    "code": 400,
                    "data": None,
                }

            # 3. 单次遍历完成：中文表头映射 + 类型转换 + 枚举转换 + 内存去重
            transformed_records: List[dict] = []
            seen_keys: Set[Tuple] = set()
            excel_duplicate_count = 0

            for record in excel_records:
                transformed = VehicleService._transform_record(record)
                if transformed is None:
                    continue
                unique_key = generate_unique_key(transformed, REPEAT_VEHICLE_FIELDS)
                if unique_key in seen_keys:
                    excel_duplicate_count += 1
                    continue
                seen_keys.add(unique_key)
                transformed_records.append(transformed)

            if not transformed_records:
                return {
                    "code": 200,
                    "message": "导入完成（所有数据均为 Excel 内部重复）",
                    "data": {
                        "msg": "无有效数据可导入",
                        "total_excel_rows": total_excel_rows,
                        "excel_duplicate_rows": excel_duplicate_count,
                        "db_duplicate_rows": 0,
                        "success_import_rows": 0,
                        "failed_import_rows": 0,
                    },
                }

            # 4. 数据库去重：一次批量查询，避免 N+1
            query_conditions = []
            for record in transformed_records:
                field_conds = []
                for field in REPEAT_VEHICLE_FIELDS:
                    value = record.get(field)
                    if isinstance(value, str):
                        value = value.strip()
                    if value is None:
                        field_conds.append(getattr(models.Vehicle, field).is_(None))
                    else:
                        field_conds.append(getattr(models.Vehicle, field) == value)
                query_conditions.append(and_(*field_conds))

            stmt = select(models.Vehicle).filter(or_(*query_conditions))
            result = await db.execute(stmt)
            existing_records = result.scalars().all()

            existing_keys: Set[Tuple] = {
                generate_unique_key(
                    {f: getattr(r, f) for f in REPEAT_VEHICLE_FIELDS},
                    REPEAT_VEHICLE_FIELDS,
                )
                for r in existing_records
            }

            final_records: List[dict] = []
            db_duplicate_count = 0
            for record in transformed_records:
                if generate_unique_key(record, REPEAT_VEHICLE_FIELDS) in existing_keys:
                    db_duplicate_count += 1
                    continue
                final_records.append(record)

            if not final_records:
                return {
                    "code": 200,
                    "message": "导入完成（所有数据已在数据库中）",
                    "data": {
                        "msg": "所有数据已存在，无需导入",
                        "total_excel_rows": total_excel_rows,
                        "excel_duplicate_rows": excel_duplicate_count,
                        "db_duplicate_rows": db_duplicate_count,
                        "success_import_rows": 0,
                        "failed_import_rows": 0,
                    },
                }

            # 5. Pydantic 校验
            valid_records: List[models.Vehicle] = []
            for idx, item_dict in enumerate(final_records):
                try:
                    validated = schemas.VehicleCreate(**item_dict)
                    valid_records.append(models.Vehicle(**validated.model_dump()))
                except Exception as e:
                    return {
                        "code": 400,
                        "message": f"第 {idx + 2} 行数据格式错误：{e}",
                        "data": None,
                    }

            # 6. 批量写入：单次 add_all + commit，事务安全
            try:
                db.add_all(valid_records)
                await db.commit()
            except Exception as e:
                await db.rollback()
                return {"code": 400, "message": f"数据库写入失败：{e}", "data": None}

            # 7. 返回结果
            return {
                "code": 200,
                "message": "文件上传并导入成功",
                "data": {
                    "msg": "批量导入完成",
                    "total_excel_rows": total_excel_rows,
                    "excel_duplicate_rows": excel_duplicate_count,
                    "db_duplicate_rows": db_duplicate_count,
                    "success_import_rows": len(final_records),
                    "failed_import_rows": 0,
                },
            }
        except Exception as e:
            return {"code": 400, "message": f"导入失败：{e}", "data": None}


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
        driver_name: Optional[str] = None,
    ) -> dict:
        stmt = select(models.BorrowRecord)
        if borrow_status:
            stmt = stmt.where(models.BorrowRecord.borrow_status == borrow_status)
        if model:
            stmt = stmt.where(models.BorrowRecord.model == model)
        if vin_code:
            stmt = stmt.where(models.BorrowRecord.vin_code.contains(vin_code))
        if driver_name:
            stmt = stmt.where(models.BorrowRecord.driver_name.contains(driver_name))

        # 统计总数
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(total_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(models.BorrowRecord.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return {
            "items": list(result.scalars().all()),
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    async def get_borrow_records(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        conditions: Optional[List[dict]] = None,
    ) -> dict:
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

        # 统计总数
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(total_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(models.BorrowRecord.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return {
            "items": list(result.scalars().all()),
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    async def get_borrow_record(
        db: AsyncSession, record_id: int
    ) -> models.BorrowRecord | str:
        record = await db.get(models.BorrowRecord, record_id)

        if not record:
            return "借用记录不存在"
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
            return "借用人不能为空"
        if not borrow.borrow_time:
            return "借用时间不能为空"
        # 检查车辆是否存在
        vehicle = await VehicleService.get_vehicle(db, borrow.vehicle_id)
        if not vehicle:
            return "车辆信息不存在"

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
        record = await BorrowService.get_borrow_record(db, record_id)
        if not record:
            return ""
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
            return "借用记录不存在"
        await db.delete(record)
        await db.commit()
        return "success"

    @staticmethod
    async def return_vehicle(db: AsyncSession, record_id: int) -> bool | str:
        record = await BorrowService.get_borrow_record(db, record_id)
        if not record:
            return "借用记录不存在"
        if record.borrow_status != "active":
            return "借用记录不是可归还的状态"

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
            return "借用记录不存在"
        if record.borrow_status != "active":
            return "借用记录不是可取消的状态"

        # 更新借用记录
        record.borrow_status = "cancelled"

        # 更新车辆状态
        vehicle = await VehicleService.get_vehicle(db, record.vehicle_id)
        vehicle.vehicle_status = models.VehicleStatus.AVAILABLE

        await db.commit()
        await db.refresh(record)
        return "success"


# ==================== 图表统计方法 ====================


class VehicleStatsService:
    """车辆统计服务 - 用于图表数据"""

    @staticmethod
    async def get_vehicle_overview(
        db: AsyncSession,
        model: Optional[str] = None,
        vin_code: Optional[str] = None,
        group: Optional[str] = None,
        vehicle_status: Optional[str] = None,
        test_status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        """获取车辆概览统计（卡片数据）"""
        # 构建筛选条件
        filters = []
        if model:
            filters.append(models.Vehicle.model.like(f"%{model}%"))
        if vin_code:
            filters.append(models.Vehicle.vin_code.like(f"%{vin_code}%"))
        if group:
            filters.append(models.Vehicle.group == group)
        if vehicle_status:
            filters.append(models.Vehicle.vehicle_status == vehicle_status)
        if test_status:
            # 支持英文枚举名和中文值两种方式
            # 例如："ALL_SUPPORT" -> TestStatus.ALL_SUPPORT 或 "支持全部测试" -> TestStatus.ALL_SUPPORT
            test_status_enum = getattr(models.TestStatus, test_status, None)
            if not test_status_enum:
                # 尝试按中文值查找枚举成员
                for member in models.TestStatus:
                    if member.value == test_status:
                        test_status_enum = member
                        break

            if test_status_enum:
                filters.append(models.Vehicle.test_status == test_status_enum)
            else:
                filters.append(models.Vehicle.test_status == test_status)

        # 总车辆数
        total_stmt = select(func.count(models.Vehicle.id))
        if filters:
            total_stmt = total_stmt.where(*filters)
        total = await db.scalar(total_stmt) or 0

        # 可用车辆数
        available_stmt = select(func.count(models.Vehicle.id)).where(
            models.Vehicle.vehicle_status == models.VehicleStatus.AVAILABLE
        )
        if filters:
            available_stmt = available_stmt.where(*filters)
        available = await db.scalar(available_stmt) or 0

        # 已借出车辆数
        borrowed_stmt = select(func.count(models.Vehicle.id)).where(
            models.Vehicle.vehicle_status == models.VehicleStatus.BORROWED
        )
        if filters:
            borrowed_stmt = borrowed_stmt.where(*filters)
        borrowed = await db.scalar(borrowed_stmt) or 0

        # 维护中车辆数
        maintenance_stmt = select(func.count(models.Vehicle.id)).where(
            models.Vehicle.vehicle_status == models.VehicleStatus.MAINTENANCE
        )
        if filters:
            maintenance_stmt = maintenance_stmt.where(*filters)
        maintenance = await db.scalar(maintenance_stmt) or 0

        return {
            "total": total,
            "available": available,
            "borrowed": borrowed,
            "maintenance": maintenance,
        }

    @staticmethod
    async def get_vehicle_utilization(
        db: AsyncSession,
        model: Optional[str] = None,
        vin_code: Optional[str] = None,
        group: Optional[str] = None,
        vehicle_status: Optional[str] = None,
        test_status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list:
        """获取每辆车的借用次数统计
        计算逻辑：
        - 每辆车的借用次数：同一车辆同一天多次借用只算一次
        - 总借用次数：所有符合条件车辆的借用次数之和
        - 占比：该车借用次数 / 总借用次数 * 100%
        """
        # 1. 构建车辆筛选条件
        vehicle_filters = []
        if model:
            vehicle_filters.append(models.Vehicle.model.like(f"%{model}%"))
        if vin_code:
            vehicle_filters.append(models.Vehicle.vin_code.like(f"%{vin_code}%"))
        if group:
            group_enum = getattr(
                models.VehicleGroup, group, None
            ) or _find_enum_by_value(models.VehicleGroup, group)
            if group_enum:
                vehicle_filters.append(models.Vehicle.group == group_enum)
            else:
                vehicle_filters.append(models.Vehicle.group == group)
        if vehicle_status:
            status_enum = getattr(
                models.VehicleStatus, vehicle_status, None
            ) or _find_enum_by_value(models.VehicleStatus, vehicle_status)
            if status_enum:
                vehicle_filters.append(models.Vehicle.vehicle_status == status_enum)
            else:
                vehicle_filters.append(models.Vehicle.vehicle_status == vehicle_status)
        if test_status:
            test_enum = getattr(
                models.TestStatus, test_status, None
            ) or _find_enum_by_value(models.TestStatus, test_status)
            if test_enum:
                vehicle_filters.append(models.Vehicle.test_status == test_enum)
            else:
                vehicle_filters.append(models.Vehicle.test_status == test_status)

        # 2. 查询符合条件的车辆
        vehicle_subq = select(
            models.Vehicle.id,
            models.Vehicle.model,
            models.Vehicle.vehicle_code,
            models.Vehicle.vin_code,
        )
        if vehicle_filters:
            vehicle_subq = vehicle_subq.where(*vehicle_filters)

        # 3. 计算每辆车的借用次数（去重：同一天多次借用算一次）
        borrow_subq = select(
            models.BorrowRecord.vehicle_id,
            func.count(func.distinct(models.BorrowRecord.borrow_time)).label(
                "borrow_count"
            ),
        )

        if start_date:
            borrow_subq = borrow_subq.where(
                models.BorrowRecord.borrow_time >= start_date
            )
        if end_date:
            borrow_subq = borrow_subq.where(models.BorrowRecord.borrow_time <= end_date)

        borrow_subq = borrow_subq.group_by(models.BorrowRecord.vehicle_id).subquery()

        # 4. 关联查询：车辆信息 + 借用次数
        # 将子查询保存到变量，避免每次调用 .subquery() 创建新对象
        vehicle_sub = vehicle_subq.subquery()

        stmt = select(
            vehicle_sub.c.id.label("vehicle_id"),
            vehicle_sub.c.model,
            vehicle_sub.c.vehicle_code,
            vehicle_sub.c.vin_code,
            func.coalesce(borrow_subq.c.borrow_count, 0).label("borrow_count"),
        ).select_from(
            vehicle_sub.outerjoin(
                borrow_subq, vehicle_sub.c.id == borrow_subq.c.vehicle_id
            )
        )

        result = await db.execute(stmt)
        vehicle_data = []
        total_borrow_count = 0

        for row in result.all():
            borrow_count = row.borrow_count
            total_borrow_count += borrow_count
            vehicle_data.append(
                {
                    "vehicle_id": row.vehicle_id,
                    "model": row.model,
                    "vehicle_code": row.vehicle_code,
                    "vin_code": row.vin_code,
                    "borrow_count": borrow_count,
                    "proportion": 0,  # 占比后续计算
                }
            )

        # 5. 计算每辆车的借用占比
        for item in vehicle_data:
            if total_borrow_count > 0:
                item["proportion"] = round(
                    item["borrow_count"] / total_borrow_count * 100, 2
                )
            else:
                item["proportion"] = 0

        # 6. 按借用次数降序排序
        vehicle_data.sort(key=lambda x: x["borrow_count"], reverse=True)

        return {
            "items": vehicle_data,
            "total_borrow_count": total_borrow_count,
            "total_vehicle_count": len(vehicle_data),
        }

    @staticmethod
    async def get_status_distribution(
        db: AsyncSession,
        model: Optional[str] = None,
        vin_code: Optional[str] = None,
        group: Optional[str] = None,
        vehicle_status: Optional[str] = None,
        test_status: Optional[str] = None,
    ) -> list:
        """获取车辆状态分布（饼图）"""
        # 构建筛选条件
        filters = []
        if model:
            filters.append(models.Vehicle.model.like(f"%{model}%"))
        if vin_code:
            filters.append(models.Vehicle.vin_code.like(f"%{vin_code}%"))
        if group:
            filters.append(models.Vehicle.group == group)
        if vehicle_status:
            filters.append(models.Vehicle.vehicle_status == vehicle_status)
        if test_status:
            # 支持英文枚举名和中文值两种方式
            # 例如："ALL_SUPPORT" -> TestStatus.ALL_SUPPORT 或 "支持全部测试" -> TestStatus.ALL_SUPPORT
            test_status_enum = getattr(models.TestStatus, test_status, None)
            if not test_status_enum:
                # 尝试按中文值查找枚举成员
                for member in models.TestStatus:
                    if member.value == test_status:
                        test_status_enum = member
                        break

            if test_status_enum:
                filters.append(models.Vehicle.test_status == test_status_enum)
            else:
                filters.append(models.Vehicle.test_status == test_status)

        stmt = select(
            models.Vehicle.vehicle_status.label("status"),
            func.count(models.Vehicle.id).label("count"),
        )

        if filters:
            stmt = stmt.where(*filters)

        stmt = stmt.group_by(models.Vehicle.vehicle_status)

        result = await db.execute(stmt)
        all_statuses = ["可借用", "已借出", "维护中"]
        status_counts = {row.status.value: row.count for row in result.all()}

        return [
            {"status": status, "count": status_counts.get(status, 0)}
            for status in all_statuses
        ]


class BorrowStatsService:
    """借用统计服务 - 用于图表数据"""

    @staticmethod
    async def get_borrow_overview(
        db: AsyncSession,
        model: Optional[str] = None,
        vin_code: Optional[str] = None,
        borrow_status: Optional[str] = None,
        driver_name: Optional[str] = None,
    ) -> dict:
        """获取借用概览统计（卡片数据）"""
        # 构建筛选条件
        filters = []
        if model:
            filters.append(models.BorrowRecord.model.like(f"%{model}%"))
        if vin_code:
            filters.append(models.BorrowRecord.vin_code.like(f"%{vin_code}%"))
        if driver_name:
            filters.append(models.BorrowRecord.driver_name.like(f"%{driver_name}%"))

        # 总借用记录数
        total_stmt = select(func.count(models.BorrowRecord.id))
        if filters:
            total_stmt = total_stmt.where(*filters)
        if borrow_status:
            total_stmt = total_stmt.where(
                models.BorrowRecord.borrow_status == borrow_status
            )
        total = await db.scalar(total_stmt) or 0

        # 借用中数量
        active_stmt = select(func.count(models.BorrowRecord.id)).where(
            models.BorrowRecord.borrow_status == "active"
        )
        if filters:
            active_stmt = active_stmt.where(*filters)
        active = await db.scalar(active_stmt) or 0

        # 已归还数量
        returned_stmt = select(func.count(models.BorrowRecord.id)).where(
            models.BorrowRecord.borrow_status == "returned"
        )
        if filters:
            returned_stmt = returned_stmt.where(*filters)
        returned = await db.scalar(returned_stmt) or 0

        # 已取消数量
        cancelled_stmt = select(func.count(models.BorrowRecord.id)).where(
            models.BorrowRecord.borrow_status == "cancelled"
        )
        if filters:
            cancelled_stmt = cancelled_stmt.where(*filters)
        cancelled = await db.scalar(cancelled_stmt) or 0

        return {
            "total": total,
            "active": active,
            "returned": returned,
            "cancelled": cancelled,
        }

    @staticmethod
    async def get_borrow_status_distribution(
        db: AsyncSession,
        model: Optional[str] = None,
        vin_code: Optional[str] = None,
        borrow_status: Optional[str] = None,
        driver_name: Optional[str] = None,
    ) -> list:
        """获取借用状态分布（饼图）"""
        # 构建筛选条件
        filters = []
        if model:
            filters.append(models.BorrowRecord.model.like(f"%{model}%"))
        if vin_code:
            filters.append(models.BorrowRecord.vin_code.like(f"%{vin_code}%"))
        if driver_name:
            filters.append(models.BorrowRecord.driver_name.like(f"%{driver_name}%"))

        stmt = select(
            models.BorrowRecord.borrow_status.label("status"),
            func.count(models.BorrowRecord.id).label("count"),
        )

        if filters:
            stmt = stmt.where(*filters)

        stmt = stmt.group_by(models.BorrowRecord.borrow_status)

        result = await db.execute(stmt)
        status_counts = {row.status: row.count for row in result.all()}

        return [
            {"status": "借用中", "count": status_counts.get("active", 0)},
            {"status": "已归还", "count": status_counts.get("returned", 0)},
            {"status": "已取消", "count": status_counts.get("cancelled", 0)},
        ]
