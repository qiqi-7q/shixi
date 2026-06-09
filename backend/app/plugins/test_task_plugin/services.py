from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from fastapi import HTTPException 
from typing import Optional
from app.plugins.test_task_plugin import models, schemas
from app.plugins.test_miles_plugin import models as miles_models
from datetime import datetime


async def calculate_achievement_rate(test_mileage: float, actual_mileage: float) -> Optional[float]:
    if test_mileage and actual_mileage and test_mileage > 0:
        rate = (actual_mileage / test_mileage) * 100
        return min(rate, 100.0)
    return None


async def calculate_mileage(test_mileage: float, actual_mileage: float) -> Optional[float]:
    if test_mileage is None and actual_mileage is None:
        return None
    if test_mileage is None:
        return actual_mileage
    if actual_mileage is None:
        return test_mileage
    return min(test_mileage, actual_mileage)


async def sync_miles_from_task(db: AsyncSession, task_data: dict):
    """
    同步任务数据到里程表
    只根据 project、vin_code、test_time 三个字段进行匹配
    """
    project = task_data.get('project')
    vin_code = task_data.get('vin_code')
    test_time = task_data.get('test_time')
    
    # 必须有 project 和 vin_code 才能匹配
    if not project or not vin_code:
        return

    # 只根据 project、vin_code、test_time 三个字段匹配
    stmt = select(miles_models.TestMiles).where(
        miles_models.TestMiles.project == project,
        miles_models.TestMiles.vin_code == vin_code
    )
    
    if test_time:
        stmt = stmt.where(miles_models.TestMiles.test_time == test_time)

    result = await db.execute(stmt)
    existing_miles = result.scalar_one_or_none()

    if existing_miles:
        # 更新现有记录
        existing_miles.project = project
        existing_miles.test_version = task_data.get('test_version')
        existing_miles.test_time = test_time
        existing_miles.vin_code = vin_code
        existing_miles.test_function = task_data.get('test_function')
        existing_miles.mileage = await calculate_mileage(
            task_data.get('test_mileage'), task_data.get('actual_mileage')
        )
        existing_miles.remarks = task_data.get('remarks')
    else:
        # 创建新记录
        db_miles = miles_models.TestMiles(
            project=project,
            test_version=task_data.get('test_version'),
            test_time=test_time,
            vin_code=vin_code,
            test_function=task_data.get('test_function'),
            mileage=await calculate_mileage(
                task_data.get('test_mileage'), task_data.get('actual_mileage')
            ),
            remarks=task_data.get('remarks')
        )
        db.add(db_miles)
        await db.flush()

    await db.commit()

async def create_test_task(db: AsyncSession, task: schemas.TestTaskCreate):
    # 计算达成率
    task_achievement_rate = await calculate_achievement_rate(
        task.test_mileage, task.actual_mileage
    )

    # 创建数据库对象
    db_task = models.TestTask(
        **task.dict(), # 从任务模型中提取所有字段
        task_achievement_rate=task_achievement_rate
    )
    db.add(db_task)
    
    # 只拿 ID，别的一概不拿
    await db.flush()
    task_id = db_task.id

    return_data = {
        "id": task_id,
        "project": task.project,
        "test_version": task.test_version,
        "test_time": task.test_time,
        "vin_code": task.vin_code,
        "test_function": task.test_function,
        "task_desc": task.task_desc,
        "task_publisher": task.task_publisher,
        "test_mileage": task.test_mileage,
        "test_person": task.test_person,
        "actual_mileage": task.actual_mileage,
        "task_achievement_rate": task_achievement_rate,
        "task_status": task.task_status,
        "reason_desc": task.reason_desc,
        "remarks": task.remarks,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    sync_data = {
        "project": task.project,
        "test_version": task.test_version,
        "test_time": task.test_time,
        "vin_code": task.vin_code,
        "test_function": task.test_function,
        "test_mileage": task.test_mileage,
        "actual_mileage": task.actual_mileage,
        "remarks": task.remarks
    }

    await db.commit()
    await sync_miles_from_task(db, sync_data)

    return schemas.TestTask(**return_data)


async def get_test_tasks(
    db: AsyncSession, skip: int = 0, limit: int = 100,
    project: str = None, test_start_date: str = None, test_end_date: str = None,
    test_function: str = None, task_publisher: str = None,
    test_person: str = None, task_status: str = None
):
    stmt = select(models.TestTask)

    if project:
        stmt = stmt.where(models.TestTask.project == project)
    if test_start_date:
        stmt = stmt.where(models.TestTask.test_time >= test_start_date)
    if test_end_date:
        stmt = stmt.where(models.TestTask.test_time <= test_end_date)
    if test_function:
        stmt = stmt.where(models.TestTask.test_function.like(f"%{test_function}%"))
    if task_publisher:
        stmt = stmt.where(models.TestTask.task_publisher == task_publisher)
    if test_person:
        stmt = stmt.where(models.TestTask.test_person == test_person)
    if task_status:
        stmt = stmt.where(models.TestTask.task_status == task_status)
    
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(total_stmt)
    total = total_result.scalar_one()

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    items = [
        schemas.TestTask(
            id=t.id, project=t.project, test_version=t.test_version,
            test_time=t.test_time, vin_code=t.vin_code,
            test_function=t.test_function, task_desc=t.task_desc,
            task_publisher=t.task_publisher, test_mileage=t.test_mileage,
            test_person=t.test_person, actual_mileage=t.actual_mileage,
            task_achievement_rate=t.task_achievement_rate,
            task_status=t.task_status, reason_desc=t.reason_desc,
            remarks=t.remarks, created_at=t.created_at, updated_at=t.updated_at
        ) for t in tasks
    ]
    
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def get_test_task(db: AsyncSession, task_id: int):
    stmt = select(models.TestTask).where(models.TestTask.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        return None

    return schemas.TestTask(
        id=task.id, project=task.project, test_version=task.test_version,
        test_time=task.test_time, vin_code=task.vin_code,
        test_function=task.test_function, task_desc=task.task_desc,
        task_publisher=task.task_publisher, test_mileage=task.test_mileage,
        test_person=task.test_person, actual_mileage=task.actual_mileage,
        task_achievement_rate=task.task_achievement_rate,
        task_status=task.task_status, reason_desc=task.reason_desc,
        remarks=task.remarks, created_at=task.created_at, updated_at=task.updated_at
    )


async def update_test_task(db: AsyncSession, task_id: int, task: schemas.TestTaskUpdate):
    stmt = select(models.TestTask).where(models.TestTask.id == task_id)
    result = await db.execute(stmt)
    db_task = result.scalar_one_or_none()
    if not db_task:
        return None

    project = db_task.project
    test_version = db_task.test_version
    test_time = db_task.test_time
    vin_code = db_task.vin_code
    test_function = db_task.test_function
    test_mileage = db_task.test_mileage
    actual_mileage = db_task.actual_mileage
    remarks = db_task.remarks

    update_data = task.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
        # 更新保存的值
        if key == 'project': project = value
        elif key == 'test_version': test_version = value
        elif key == 'test_time': test_time = value
        elif key == 'vin_code': vin_code = value
        elif key == 'test_function': test_function = value
        elif key == 'test_mileage': test_mileage = value
        elif key == 'actual_mileage': actual_mileage = value
        elif key == 'remarks': remarks = value

    task_achievement_rate = await calculate_achievement_rate(
        db_task.test_mileage, db_task.actual_mileage
    )
    db_task.task_achievement_rate = task_achievement_rate

    await db.commit()

    task_data = {
        "project": project,
        "test_version": test_version,
        "test_time": test_time,
        "vin_code": vin_code,
        "test_function": test_function,
        "test_mileage": test_mileage,
        "actual_mileage": actual_mileage,
        "remarks": remarks
    }
    await sync_miles_from_task(db, task_data)

    # 重新查询获取更新后的数据
    stmt = select(models.TestTask).where(models.TestTask.id == task_id)
    result = await db.execute(stmt)
    updated_task = result.scalar_one()

    return schemas.TestTask(
        id=updated_task.id, project=updated_task.project, test_version=updated_task.test_version,
        test_time=updated_task.test_time, vin_code=updated_task.vin_code,
        test_function=updated_task.test_function, task_desc=updated_task.task_desc,
        task_publisher=updated_task.task_publisher, test_mileage=updated_task.test_mileage,
        test_person=updated_task.test_person, actual_mileage=updated_task.actual_mileage,
        task_achievement_rate=updated_task.task_achievement_rate,
        task_status=updated_task.task_status, reason_desc=updated_task.reason_desc,
        remarks=updated_task.remarks, created_at=updated_task.created_at, updated_at=updated_task.updated_at
    )


async def delete_test_task(db: AsyncSession, task_id: int):
    stmt = select(models.TestTask).where(models.TestTask.id == task_id)
    result = await db.execute(stmt)
    db_task = result.scalar_one_or_none()
    if not db_task:
        return None

    project = db_task.project
    vin_code = db_task.vin_code
    test_time = db_task.test_time

    # 先删除关联的里程记录（只根据 project、vin_code、test_time 匹配）
    delete_stmt = delete(miles_models.TestMiles).where(
        miles_models.TestMiles.project == project,
        miles_models.TestMiles.vin_code == vin_code
    )
    if test_time:
        delete_stmt = delete_stmt.where(miles_models.TestMiles.test_time == test_time)

    await db.execute(delete_stmt)
    await db.delete(db_task)
    await db.commit()

    return {"msg": "删除成功"}


# ==================== 统计相关函数 ====================
from sqlalchemy import func


async def get_daily_task_count(db: AsyncSession, start_date: str = None, end_date: str = None):
    """获取每日任务下发量"""
    stmt = select(
        func.date(models.TestTask.created_at).label('date'),
        func.count(models.TestTask.id).label('count')
    )
    
    if start_date:
        stmt = stmt.where(models.TestTask.created_at >= start_date)
    if end_date:
        stmt = stmt.where(models.TestTask.created_at <= end_date)
    
    stmt = stmt.group_by(func.date(models.TestTask.created_at)).order_by(func.date(models.TestTask.created_at))
    
    result = await db.execute(stmt)
    return [{"date": str(row.date), "count": row.count} for row in result.all()]


async def get_task_status_count(db: AsyncSession, project: str = None):
    """获取任务状态分布"""
    stmt = select(
        models.TestTask.task_status.label('status'),
        func.count(models.TestTask.id).label('count')
    )
    
    if project:
        stmt = stmt.where(models.TestTask.project == project)
    
    stmt = stmt.group_by(models.TestTask.task_status)
    
    result = await db.execute(stmt)
    status_counts = {row.status: row.count for row in result.all()}
    
    # 确保返回所有5个状态，默认为0
    all_statuses = ["完成", "进行中", "未开始", "未达标", "挂起"]
    return [{"status": status, "count": status_counts.get(status, 0)} for status in all_statuses]


async def get_function_task_count(db: AsyncSession, project: str = None):
    """获取各功能任务量"""
    stmt = select(
        models.TestTask.test_function.label('function'),
        func.count(models.TestTask.id).label('count')
    )
    
    if project:
        stmt = stmt.where(models.TestTask.project == project)
    
    stmt = stmt.group_by(models.TestTask.test_function).order_by(func.count(models.TestTask.id).desc())
    
    result = await db.execute(stmt)
    return [{"function": row.function or "未分类", "count": row.count} for row in result.all()]


async def get_task_stats(db: AsyncSession, start_date: str = None, end_date: str = None, project: str = None):
    """获取任务统计数据（包含所有统计信息）"""
    daily_counts = await get_daily_task_count(db, start_date, end_date)
    status_counts = await get_task_status_count(db, project)
    function_counts = await get_function_task_count(db, project)
    
    return {
        "daily_counts": daily_counts,
        "status_counts": status_counts,
        "function_counts": function_counts
    }