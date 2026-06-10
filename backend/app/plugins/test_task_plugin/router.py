from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from datetime import datetime
from app.plugins.test_task_plugin import schemas, services

router = APIRouter()


@router.post("/")
async def create_task(task: schemas.TestTaskCreate, db: AsyncSession = Depends(get_db)):
    result = await services.create_test_task(db=db, task=task)
    return {"code": 200, "data": result, "message": "任务创建成功"}


@router.get("/")
async def get_tasks(
    skip: int = Query(0, description="跳过的记录数，用于分页"),
    limit: int = Query(10, description="每页显示的记录数"),
    project: str = Query(None, description="按项目精准筛选"),
    test_start_date: str = Query(None, description="按测试开始时间精准筛选"),
    test_end_date: str = Query(None, description="按测试结束时间精准筛选"),
    test_function: str = Query(None, description="按测试功能精准筛选"),
    task_publisher: str = Query(None, description="按任务发布人精准筛选"),
    test_person: str = Query(None, description="按测试人员精准筛选"),
    task_status: str = Query(None, description="按任务状态精准筛选"),
    db: AsyncSession = Depends(get_db)
):
    result = await services.get_test_tasks(
        db, 
        skip=skip, 
        limit=limit,
        project=project,
        test_start_date=test_start_date,
        test_end_date=test_end_date,
        test_function=test_function,
        task_publisher=task_publisher,
        test_person=test_person,
        task_status=task_status
    )
    return {"code": 200, "data": result, "message": "任务列表获取成功"}


@router.get("/{task_id}")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.get_test_task(db, task_id=task_id)
    if result:
        return {"code": 200, "data": result, "message": "任务获取成功"}
    return {"code": 404, "data": None, "message": "任务不存在"}


@router.put("/{task_id}")
async def update_task(task_id: int, task: schemas.TestTaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await services.update_test_task(db, task_id=task_id, task=task)
    if result:
        return {"code": 200, "data": result, "message": "任务更新成功"}
    return {"code": 404, "data": None, "message": "任务不存在"}


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await services.delete_test_task(db, task_id=task_id)
    if result:
        return {"code": 200, "data": result, "message": "任务删除成功"}
    return {"code": 404, "data": None, "message": "任务不存在"}


# ==================== 统计接口 ====================
@router.get("/stats/")
async def get_task_stats(
    start_date: str = Query(None, description="统计开始日期（格式：YYYY-MM-DD）"),
    end_date: str = Query(None, description="统计结束日期（格式：YYYY-MM-DD）"),
    project: str = Query(None, description="按项目筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取任务统计数据"""
    result = await services.get_task_stats(db, start_date=start_date, end_date=end_date, project=project)
    return {"code": 200, "data": result, "message": "任务统计数据获取成功"}


@router.get("/stats/daily")
async def get_daily_task_count(
    start_date: str = Query(None, description="统计开始日期（格式：YYYY-MM-DD）"),
    end_date: str = Query(None, description="统计结束日期（格式：YYYY-MM-DD）"),
    db: AsyncSession = Depends(get_db)
):
    """获取每日任务下发量"""
    result = await services.get_daily_task_count(db, start_date, end_date)
    return {"code": 200, "data": {"daily_counts": result}, "message": "每日任务下发量获取成功"}


@router.get("/stats/status")
async def get_task_status_count(
    project: str = Query(None, description="按项目筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取任务状态分布"""
    result = await services.get_task_status_count(db, project)
    return {"code": 200, "data": {"status_counts": result}, "message": "任务状态分布获取成功"}


@router.get("/stats/function")
async def get_function_task_count(
    project: str = Query(None, description="按项目筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取各功能任务量"""
    result = await services.get_function_task_count(db, project)
    return {"code": 200, "data": {"function_counts": result}, "message": "各功能任务量获取成功"}
