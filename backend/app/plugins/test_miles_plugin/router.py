from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.plugins.test_miles_plugin import schemas, services
from datetime import datetime

router = APIRouter()


@router.post("/")
async def create_miles(data: schemas.TestMilesCreate, db: AsyncSession = Depends(get_db)):
    result = await services.create_test_miles(db=db, data=data)
    return {"code": 200, "data": result, "message": "里程记录创建成功"}


@router.get("/")
async def get_miles_list(
    skip: int = Query(0, description="跳过的记录数，用于分页"),
    limit: int = Query(10, description="每页显示的记录数"),
    project: str = Query(None, description="按项目精准筛选"),
    test_version: str = Query(None, description="按测试版本模糊筛选"),
    test_function: str = Query(None, description="按测试功能精准筛选"),
    test_start_date: str = Query(None, description="按测试开始时间精准筛选"),
    test_end_date: str = Query(None, description="按测试结束时间精准筛选"),
    db: AsyncSession = Depends(get_db)
):
    result = await services.get_test_miles_list(db, skip=skip, limit=limit, project=project, test_version=test_version, test_function=test_function, test_start_date=test_start_date, test_end_date=test_end_date)
    return {"code": 200, "data": result, "message": "获取里程记录列表成功"}


@router.get("/{miles_id}")
async def get_miles(miles_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.get_test_miles(db, miles_id=miles_id)
    if result:
        return {"code": 200, "data": result, "message": "获取里程记录成功"}
    return {"code": 404, "data": None, "message": "里程记录不存在"}


@router.put("/{miles_id}")
async def update_miles(miles_id: int, data: schemas.TestMilesUpdate, db: AsyncSession = Depends(get_db)):
    result = await services.update_test_miles(db, miles_id=miles_id, data=data)
    if result:
        return {"code": 200, "data": result, "message": "更新里程记录成功"}
    return {"code": 404, "data": None, "message": "里程记录不存在"}


@router.delete("/{miles_id}")
async def delete_miles(miles_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.delete_test_miles(db, miles_id=miles_id)
    if result:
        return {"code": 200, "data": result, "message": "删除成功"}
    return {"code": 404, "data": None, "message": "里程记录不存在"}


# ==================== 统计接口 ====================
@router.get("/stats/")
async def get_mileage_stats(
    start_date: str = Query(None, description="统计开始日期（格式：YYYY-MM-DD）"),
    end_date: str = Query(None, description="统计结束日期（格式：YYYY-MM-DD）"),
    project: str = Query(None, description="按项目名称筛选"),
    test_version: str = Query(None, description="按测试版本筛选（模糊匹配）"),
    test_function: str = Query(None, description="按测试功能筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取里程统计数据（包含总览、版本、每日、功能统计）"""
    result = await services.get_mileage_stats(db, start_date=start_date, end_date=end_date, project=project, test_version=test_version, test_function=test_function)
    return {"code": 200, "data": result, "message": "获取里程统计数据成功"}


@router.get("/stats/version")
async def get_version_mileage(
    project: str = Query(None, description="按项目名称筛选"),
    test_version: str = Query(None, description="按测试版本筛选（模糊匹配）"),
    test_function: str = Query(None, description="按测试功能筛选"),
    start_date: str = Query(None, description="统计开始日期（格式：YYYY-MM-DD）"),
    end_date: str = Query(None, description="统计结束日期（格式：YYYY-MM-DD）"),
    db: AsyncSession = Depends(get_db)
):
    """获取版本里程统计"""
    result = await services.get_version_mileage(db, project=project, test_version=test_version, test_function=test_function, start_date=start_date, end_date=end_date)
    return {"code": 200, "data": {"version_mileage": result}, "message": "获取版本里程统计成功"}


@router.get("/stats/daily")
async def get_daily_mileage(
    start_date: str = Query(None, description="统计开始日期（格式：YYYY-MM-DD）"),
    end_date: str = Query(None, description="统计结束日期（格式：YYYY-MM-DD）"),
    project: str = Query(None, description="按项目名称筛选"),
    test_version: str = Query(None, description="按测试版本筛选（模糊匹配）"),
    test_function: str = Query(None, description="按测试功能筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取每日里程统计"""
    result = await services.get_daily_mileage(db, start_date=start_date, end_date=end_date, project=project, test_version=test_version, test_function=test_function)
    return {"code": 200, "data": {"daily_mileage": result}, "message": "获取每日里程统计成功"}


@router.get("/stats/function")
async def get_function_mileage(
    project: str = Query(None, description="按项目名称筛选"),
    test_version: str = Query(None, description="按测试版本筛选（模糊匹配）"),
    test_function: str = Query(None, description="按测试功能筛选"),
    start_date: str = Query(None, description="统计开始日期（格式：YYYY-MM-DD）"),
    end_date: str = Query(None, description="统计结束日期（格式：YYYY-MM-DD）"),
    db: AsyncSession = Depends(get_db)
):
    """获取功能里程统计"""
    result = await services.get_function_mileage(db, project=project, test_version=test_version, test_function=test_function, start_date=start_date, end_date=end_date)
    return {"code": 200, "data": {"function_mileage": result}, "message": "获取功能里程统计成功"}
