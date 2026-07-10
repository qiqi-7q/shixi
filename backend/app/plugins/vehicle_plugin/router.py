import time
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.plugins.auth_plugin.models import User
from app.plugins.auth_plugin.router import get_current_user
from app.plugins.vehicle_plugin import models, schemas, services

router = APIRouter()


# ============= 静态路由放在前面 =============
@router.get("/models")
async def get_vehicle_models(
    db: AsyncSession = Depends(get_db),
):
    """获取所有车型"""
    model_list = await services.VehicleService.get_vehicle_models(db)
    return {"data": model_list}

@router.get("/model_distribution")
async def get_model_distribution(
    db: AsyncSession = Depends(get_db),
):
    """获取车型分布"""
    model_list = await services.VehicleService.model_distribution(db)
    return {"data": model_list, "message": "success", "code": 200}

@router.get("/stats/overview")
async def get_vehicle_overview(
    db: AsyncSession = Depends(get_db),
    model: Optional[str] = Query(None, description="车型"),
    vin_code: Optional[str] = Query(None, description="VIN码"),
    group: Optional[str] = Query(None, description="组别（行车组/泊车组/预警组）"),
    vehicle_status: Optional[str] = Query(
        None, description="使用状态（可借用/已借出/维护中/已预定）"
    ),
    test_status: Optional[str] = Query(None, description="车辆状态"),
):
    """获取车辆概览统计（卡片数据）"""
    stats = await services.VehicleStatsService.get_vehicle_overview(
        db,
        model=model,
        vin_code=vin_code,
        group=group,
        vehicle_status=vehicle_status,
        test_status=test_status,
    )
    return {"data": stats, "message": "success", "code": 200}


@router.get("/stats/utilization")
async def get_vehicle_utilization(
    db: AsyncSession = Depends(get_db),
    model: Optional[str] = Query(None, description="车型（模糊匹配）"),
    vin_code: Optional[str] = Query(None, description="VIN码（模糊匹配）"),
    group: Optional[str] = Query(None, description="组别（行车组/泊车组/预警组）"),
    vehicle_status: Optional[str] = Query(
        None, description="使用状态（可借用/已借出/维护中/已预定）"
    ),
    test_status: Optional[str] = Query(None, description="车辆状态"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
):
    """获取每辆车的借用次数统计
    统计逻辑：
    - 每辆车的借用次数：同一车辆同一天多次借用只算一次
    - 占比：该车借用次数 / 总借用次数 * 100%
    """
    data = await services.VehicleStatsService.get_vehicle_utilization(
        db,
        model=model,
        vin_code=vin_code,
        group=group,
        vehicle_status=vehicle_status,
        test_status=test_status,
        start_date=start_date,
        end_date=end_date,
    )
    return {"data": data, "message": "success", "code": 200}


@router.get("/stats/status_distribution")
async def get_status_distribution(
    db: AsyncSession = Depends(get_db),
    model: Optional[str] = Query(None, description="车型"),
    vin_code: Optional[str] = Query(None, description="VIN码"),
    group: Optional[str] = Query(None, description="组别（行车组/泊车组/预警组）"),
    vehicle_status: Optional[str] = Query(
        None, description="使用状态（可借用/已借出/维护中/已预定）"
    ),
    test_status: Optional[str] = Query(None, description="车辆状态"),
):
    """获取车辆状态分布（饼图）"""
    data = await services.VehicleStatsService.get_status_distribution(
        db,
        model=model,
        vin_code=vin_code,
        group=group,
        vehicle_status=vehicle_status,
        test_status=test_status,
    )
    return {"data": data, "message": "success", "code": 200}


# ============= 列表路由 =============
# 时间字段只支持 between/not_between 操作符
TIME_FIELDS = {"created_at", "updated_at"}


@router.post("/advsearch")
async def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    conditions: Optional[List[dict]] = None,
    sort_by: Optional[str] = Query(None, description="排序字段名（不提供则不排序）"),
    sort_order: Optional[str] = Query(
        "asc", description="排序方向：asc（升序，默认）/ desc（降序）"
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取车辆列表（高级查询）"""

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

            if field_name not in schemas.VEHICLE_WHITELIST:
                return {
                    "message": f"无效的字段: {field_name} ",
                    "code": 400,
                }
            if operator not in settings.ADVANCED_OPERATORS:
                return {
                    "message": f"无效的操作: {operator} ",
                    "code": 400,
                }

    vehicleData = await services.VehicleService.get_vehicles(
        db,
        skip=skip,
        limit=limit,
        conditions=conditions,
        sort_by=sort_by,
        sort_order=sort_order,
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
        return {"message": "车辆信息创建成功", "code": 200, "data": None}
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
        return {"message": "车辆信息更新成功", "code": 200, "data": None}
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
        return {"message": "车辆信息删除成功", "code": 200, "data": None}
    else:
        return {"message": result, "code": 400, "data": None}


# 6. 批量本地数据导入（核心功能）
@router.post("/vehicle_import")
async def vehicle_import(file: UploadFile, db: AsyncSession = Depends(get_db)):
    """
    批量本地数据导入（上传Excel文件）
    """
    result = await services.VehicleService.process_vehicle_excel_upload(file, db)
    return result


borrow_router = APIRouter()


# ============= 静态路由 =============
@borrow_router.get("/stats/overview")
async def get_borrow_overview(
    db: AsyncSession = Depends(get_db),
    model: Optional[str] = Query(None, description="车型"),
    vin_code: Optional[str] = Query(None, description="VIN码"),
    borrow_status: Optional[str] = Query(
        None, description="借用状态（borrowing/returned/cancelled/reserved）"
    ),
    driver_name: Optional[str] = Query(None, description="司机姓名"),
):
    """获取借用概览统计（卡片数据）"""
    stats = await services.BorrowStatsService.get_borrow_overview(
        db,
        model=model,
        vin_code=vin_code,
        borrow_status=borrow_status,
        driver_name=driver_name,
    )
    return {"data": stats, "message": "success", "code": 200}


@borrow_router.get("/stats/status_distribution")
async def get_borrow_status_distribution(
    db: AsyncSession = Depends(get_db),
    model: Optional[str] = Query(None, description="车型"),
    vin_code: Optional[str] = Query(None, description="VIN码"),
    borrow_status: Optional[str] = Query(
        None, description="借用状态（borrowing/returned/cancelled/reserved）"
    ),
    driver_name: Optional[str] = Query(None, description="司机姓名"),
):
    """获取借用状态分布（饼图）"""
    data = await services.BorrowStatsService.get_borrow_status_distribution(
        db,
        model=model,
        vin_code=vin_code,
        borrow_status=borrow_status,
        driver_name=driver_name,
    )
    return {"data": data, "message": "success", "code": 200}


# ============= 列表路由 =============
# 借用记录时间字段
BORROW_TIME_FIELDS = {"created_at", "updated_at", "borrow_time"}


@borrow_router.post("/advsearch")
async def get_borrow_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    conditions: Optional[List[dict]] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取借用记录列表（高级查询）"""

    if conditions:
        for cond in conditions:
            field_name = cond["advanced_field"]
            operator = cond["advanced_operator"]

            # 时间字段只支持 between/not_between 操作符
            if field_name in BORROW_TIME_FIELDS and operator not in (
                "between",
                "not_between",
            ):
                return {
                    "message": f"时间字段 {field_name} 只支持 between/not_between 操作符",
                    "code": 400,
                    "data": None,
                }

            # between/not_between 的值必须是数组
            if operator in ("between", "not_between"):
                if (
                    not isinstance(cond.get("advanced_value"), list)
                    or len(cond["advanced_value"]) != 2
                ):
                    return {
                        "message": f"操作符 {operator} 的值必须是包含两个元素的数组",
                        "code": 400,
                        "data": None,
                    }
                # 时间字段特殊处理：将结束日期调整为当天的 23:59:59
                if field_name in TIME_FIELDS:

                    start_value = cond["advanced_value"][0]
                    end_value = cond["advanced_value"][1]

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

            if field_name not in schemas.BORROW_WHITELIST:
                return {
                    "message": f"无效的字段: {field_name} ",
                    "code": 400,
                    "data": None,
                }
            if operator not in settings.ADVANCED_OPERATORS:
                return {
                    "message": f"无效的操作: {operator} ",
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


@borrow_router.post("/borrowed")
async def borrowed_records(
    record_id: int,
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取除当前记录外的借用记录，并返回借用人和借用时间供借车时判断"""
    existing_borrows = await services.BorrowService.borrowed_records(
        db, record_id, vehicle_id
    )
    return {"data": existing_borrows, "message": "success", "code": 200}


@borrow_router.post("/borrowedriver")
async def borrow_driver(
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """获取内照处于有效期内的司机的id和姓名,以当前日期为准,根据id asc排序"""
    dr_re = await services.BorrowService.get_dcv(db)
    return {"data": dr_re, "message": "success", "code": 200}


@borrow_router.post("/createborrow")
async def create_borrow_record(
    borrow: schemas.BorrowRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建借用记录"""
    # if not current_user:
    #     return {"message": "token已失效，请重新登录", "code": 401, "data": None}
    result = await services.BorrowService.create_borrow_record(db, borrow, current_user)
    if result == "success":
        return {
            "message": "借用记录创建成功",
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
            "message": "借用记录更新成功",
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
            "message": "借用记录删除成功",
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
        return {"message": "车辆已归还", "code": 200, "data": None}
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
            "message": "借用记录取消成功",
            "code": 200,
            "data": None,
        }
    else:
        return {"message": result, "code": 400, "data": None}
