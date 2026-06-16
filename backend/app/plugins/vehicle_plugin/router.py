from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.plugins.vehicle_plugin import models, schemas, services

router = APIRouter()


# ============= 静态路由放在前面 =============


@router.get("/stats/overview")
async def get_vehicle_overview(
        db: AsyncSession = Depends(get_db),
        model: Optional[str] = Query(None, description="车型"),
        vin_code: Optional[str] = Query(None, description="VIN码"),
        group: Optional[str] = Query(None, description="组别（行车组/泊车组/预警组）"),
        vehicle_status: Optional[str] = Query(None, description="车辆状态（可借用/已借出/维护中）"),
        test_status: Optional[str] = Query(None, description="测试状态"),
        start_date: Optional[str] = Query(None, description="统计起始日期（格式：YYYY-MM-DD）"),
        end_date: Optional[str] = Query(None, description="统计截止日期（格式：YYYY-MM-DD）"),
):
    """获取车辆概览统计（卡片数据）"""
    stats = await services.VehicleStatsService.get_vehicle_overview(
        db, model=model, vin_code=vin_code, group=group, vehicle_status=vehicle_status, 
        test_status=test_status, start_date=start_date, end_date=end_date
    )
    return {"data": stats, "message": "success", "code": 200}


@router.get("/stats/utilization")
async def get_vehicle_utilization(
        db: AsyncSession = Depends(get_db),
        model: Optional[str] = Query(None, description="车型（模糊匹配）"),
        vin_code: Optional[str] = Query(None, description="VIN码（模糊匹配）"),
        group: Optional[str] = Query(None, description="组别（行车组/泊车组/预警组）"),
        vehicle_status: Optional[str] = Query(None, description="车辆状态（可借用/已借出/维护中）"),
        test_status: Optional[str] = Query(None, description="测试状态"),
        start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)")
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
        end_date=end_date
    )
    return {"data": data, "message": "success", "code": 200}


@router.get("/stats/status_distribution")
async def get_status_distribution(
        db: AsyncSession = Depends(get_db),
        model: Optional[str] = Query(None, description="车型"),
        vin_code: Optional[str] = Query(None, description="VIN码"),
        group: Optional[str] = Query(None, description="组别（行车组/泊车组/预警组）"),
        vehicle_status: Optional[str] = Query(None, description="车辆状态（可借用/已借出/维护中）"),
        test_status: Optional[str] = Query(None, description="测试状态"),
):
    """获取车辆状态分布（饼图）"""
    data = await services.VehicleStatsService.get_status_distribution(
        db, model=model, vin_code=vin_code, group=group, vehicle_status=vehicle_status, test_status=test_status
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
        db: AsyncSession = Depends(get_db),
):
    """获取车辆列表（高级查询）"""

    if conditions:
        for cond in conditions:
            field_name = cond["advanced_field"]
            operator = cond["advanced_operator"]

            # 时间字段只支持 between/not_between 操作符
            if field_name in TIME_FIELDS and operator not in ("between", "not_between"):
                return {
                    "message": f"时间字段 {field_name} 只支持 between/not_between 操作符",
                    "code": 400,
                }

            # between/not_between 的值必须是数组
            if operator in ("between", "not_between"):
                if not isinstance(cond.get("advanced_value"), list) or len(cond["advanced_value"]) != 2:
                    return {
                        "message": f"操作符 {operator} 的值必须是包含两个元素的数组",
                        "code": 400,
                    }

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
    )
    return {"data": vehicleData, "message": "success", "code": 200}


@router.get("/fixsearch")
async def get_vehicles_simple(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        vehicle_status: Optional[str] = None,
        vin_code: Optional[str] = None,
        group: Optional[str] = None,
        model: Optional[str] = None,
        test_status: Optional[str] = None,
        db: AsyncSession = Depends(get_db)
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
        test_status=test_status
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


borrow_router = APIRouter()


# ============= 静态路由 =============
@borrow_router.get("/stats/overview")
async def get_borrow_overview(
        db: AsyncSession = Depends(get_db),
        model: Optional[str] = Query(None, description="车型"),
        vin_code: Optional[str] = Query(None, description="VIN码"),
        borrow_status: Optional[str] = Query(None, description="借用状态（active/returned/cancelled）"),
        driver_name: Optional[str] = Query(None, description="司机姓名"),
):
    """获取借用概览统计（卡片数据）"""
    stats = await services.BorrowStatsService.get_borrow_overview(
        db, model=model, vin_code=vin_code, borrow_status=borrow_status, driver_name=driver_name
    )
    return {"data": stats, "message": "success", "code": 200}


@borrow_router.get("/stats/status_distribution")
async def get_borrow_status_distribution(
        db: AsyncSession = Depends(get_db),
        model: Optional[str] = Query(None, description="车型"),
        vin_code: Optional[str] = Query(None, description="VIN码"),
        borrow_status: Optional[str] = Query(None, description="借用状态（active/returned/cancelled）"),
        driver_name: Optional[str] = Query(None, description="司机姓名"),
):
    """获取借用状态分布（饼图）"""
    data = await services.BorrowStatsService.get_borrow_status_distribution(
        db, model=model, vin_code=vin_code, borrow_status=borrow_status, driver_name=driver_name
    )
    return {"data": data, "message": "success", "code": 200}


# ============= 列表路由 =============
@borrow_router.get("/fixsearch")
async def get_borrow_records_simple(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        model: Optional[str] = None,
        vin_code: Optional[str] = None,
        borrow_status: Optional[str] = None,
        db: AsyncSession = Depends(get_db),
        driver_name: Optional[str] = None
):
    """获取借用记录列表"""
    records = await services.BorrowService.get_borrow_records_simple(
        db,
        skip=skip,
        limit=limit,
        model=model,
        vin_code=vin_code,
        borrow_status=borrow_status,
        driver_name=driver_name
    )
    return {"data": records, "message": "success", "code": 200}


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
            if field_name in BORROW_TIME_FIELDS and operator not in ("between", "not_between"):
                return {
                    "message": f"时间字段 {field_name} 只支持 between/not_between 操作符",
                    "code": 400,
                    "data": None,
                }

            # between/not_between 的值必须是数组
            if operator in ("between", "not_between"):
                if not isinstance(cond.get("advanced_value"), list) or len(cond["advanced_value"]) != 2:
                    return {
                        "message": f"操作符 {operator} 的值必须是包含两个元素的数组",
                        "code": 400,
                        "data": None,
                    }

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
