from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from app.plugins.test_miles_plugin import models, schemas
from datetime import datetime


async def create_test_miles(db: AsyncSession, data: schemas.TestMilesCreate):
    db_miles = models.TestMiles(**data.dict())
    db.add(db_miles)
    await db.commit()
    await db.refresh(db_miles)
    return db_miles

async def get_current_project(db: AsyncSession):
    stmt = select(models.TestMiles.project).distinct()
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_test_miles_list(db: AsyncSession, skip: int = 0, limit: int = 100, project: str = None, test_version: str = None, test_function: str = None, test_start_date: str = None, test_end_date: str = None):
    """获取测试里程列表，支持分页和筛选条件"""
    stmt = select(models.TestMiles)
    
    if project:
        stmt = stmt.where(models.TestMiles.project == project)
    
    if test_version:
        stmt = stmt.where(models.TestMiles.test_version.like(f"%{test_version}%"))
    
    if test_function:
        stmt = stmt.where(models.TestMiles.test_function == test_function )
    
    if test_start_date:
        stmt = stmt.where(models.TestMiles.test_time >= test_start_date)
    
    if test_end_date:
        stmt = stmt.where(models.TestMiles.test_time <= test_end_date)
    
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(total_stmt)
    total = total_result.scalar_one()
    
    stmt = stmt.offset(skip).limit(limit).order_by(models.TestMiles.id.desc())
    result = await db.execute(stmt)
    
    return {
        "items": result.scalars().all(),
        "total": total,
        "skip": skip,
        "limit": limit
    }


async def get_test_miles(db: AsyncSession, miles_id: int):
    stmt = select(models.TestMiles).where(models.TestMiles.id == miles_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        return None
    return item


async def update_test_miles(db: AsyncSession, miles_id: int, data: schemas.TestMilesUpdate):
    stmt = select(models.TestMiles).where(models.TestMiles.id == miles_id)
    result = await db.execute(stmt)
    db_miles = result.scalar_one_or_none()
    if not db_miles:
        return None

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_miles, key, value)

    await db.commit()
    await db.refresh(db_miles)
    return db_miles


async def delete_test_miles(db: AsyncSession, miles_id: int):
    stmt = select(models.TestMiles).where(models.TestMiles.id == miles_id)
    result = await db.execute(stmt)
    db_miles = result.scalar_one_or_none()
    if not db_miles:
        return None
    await db.delete(db_miles)
    await db.commit()
    return {"msg": "删除成功"}


# ==================== 统计相关函数 ====================


async def get_version_mileage(db: AsyncSession, project: str = None, test_version: str = None, test_function: str = None, start_date: str = None, end_date: str = None):
    """获取版本里程统计"""
    stmt = select(
        models.TestMiles.test_version.label('version'),
        func.sum(models.TestMiles.mileage).label('total_mileage')
    )
    
    if project:
        stmt = stmt.where(models.TestMiles.project == project)
    if test_version:
        stmt = stmt.where(models.TestMiles.test_version.like(f"%{test_version}%"))
    if test_function:
        stmt = stmt.where(models.TestMiles.test_function == test_function)
    if start_date:
        stmt = stmt.where(models.TestMiles.test_time >= start_date)
    if end_date:
        stmt = stmt.where(models.TestMiles.test_time <= end_date)
    
    stmt = stmt.group_by(models.TestMiles.test_version).order_by(func.sum(models.TestMiles.mileage).desc())
    
    result = await db.execute(stmt)
    return [{"version": row.version or "未分类", "total_mileage": float(row.total_mileage or 0)} for row in result.all()]


async def get_daily_mileage(db: AsyncSession, start_date: str = None, end_date: str = None, project: str = None, test_version: str = None, test_function: str = None):
    """获取每日里程统计"""
    stmt = select(
        func.date(models.TestMiles.test_time).label('date'),
        func.sum(models.TestMiles.mileage).label('total_mileage')
    )
    
    if project:
        stmt = stmt.where(models.TestMiles.project == project)
    if test_version:
        stmt = stmt.where(models.TestMiles.test_version.like(f"%{test_version}%"))
    if test_function:
        stmt = stmt.where(models.TestMiles.test_function == test_function)
    if start_date:
        stmt = stmt.where(models.TestMiles.test_time >= start_date)
    if end_date:
        stmt = stmt.where(models.TestMiles.test_time <= end_date)
    
    stmt = stmt.group_by(func.date(models.TestMiles.test_time)).order_by(func.date(models.TestMiles.test_time))
    
    result = await db.execute(stmt)
    return [{"date": str(row.date), "total_mileage": float(row.total_mileage or 0)} for row in result.all()]


async def get_function_mileage(db: AsyncSession, project: str = None, test_version: str = None, test_function: str = None, start_date: str = None, end_date: str = None):
    """获取功能里程统计"""
    stmt = select(
        models.TestMiles.test_function.label('function'),
        func.sum(models.TestMiles.mileage).label('total_mileage')
    )
    
    if project:
        stmt = stmt.where(models.TestMiles.project == project)
    if test_version:
        stmt = stmt.where(models.TestMiles.test_version.like(f"%{test_version}%"))
    if test_function:
        stmt = stmt.where(models.TestMiles.test_function == test_function)
    if start_date:
        stmt = stmt.where(models.TestMiles.test_time >= start_date)
    if end_date:
        stmt = stmt.where(models.TestMiles.test_time <= end_date)
    
    stmt = stmt.group_by(models.TestMiles.test_function).order_by(func.sum(models.TestMiles.mileage).desc())
    
    result = await db.execute(stmt)
    return [{"function": row.function or "未分类", "total_mileage": float(row.total_mileage or 0)} for row in result.all()]


async def get_mileage_stats(db: AsyncSession, start_date: str = None, end_date: str = None, project: str = None, test_version: str = None, test_function: str = None):
    """获取里程统计数据（包含所有统计信息）"""
    version_mileage = await get_version_mileage(db, project, test_version, test_function, start_date, end_date)
    daily_mileage = await get_daily_mileage(db, start_date, end_date, project, test_version, test_function)
    function_mileage = await get_function_mileage(db, project, test_version, test_function, start_date, end_date)
    overview = await get_mileage_overview(db, start_date, end_date, project, test_version, test_function)
    
    return {
        "overview": overview,
        "version_mileage": version_mileage,
        "daily_mileage": daily_mileage,
        "function_mileage": function_mileage
    }


async def get_mileage_overview(db: AsyncSession, start_date: str = None, end_date: str = None, project: str = None, test_version: str = None, test_function: str = None):
    """获取里程总览统计（总记录数、总里程、NAP、CNAP）"""

    stmt = select(
        func.count(models.TestMiles.id).label('total_records'),
        func.sum(models.TestMiles.mileage).label('total_mileage'),
        func.sum(func.IF(models.TestMiles.test_function == 'NAP', models.TestMiles.mileage, 0)).label('nap'),
        func.sum(func.IF(models.TestMiles.test_function == 'CNAP', models.TestMiles.mileage, 0)).label('cnap')
    )
    
    if project:
        stmt = stmt.where(models.TestMiles.project == project)
    if test_version:
        stmt = stmt.where(models.TestMiles.test_version.like(f"%{test_version}%"))
    if test_function:
        stmt = stmt.where(models.TestMiles.test_function == test_function)
    if start_date:
        stmt = stmt.where(models.TestMiles.test_time >= start_date)
    if end_date:
        stmt = stmt.where(models.TestMiles.test_time <= end_date)
    
    result = await db.execute(stmt)
    row = result.one()
    
    return {
        "total_records": int(row.total_records or 0),
        "total_mileage": float(row.total_mileage or 0),
        "nap": float(row.nap or 0),
        "cnap": float(row.cnap or 0)
    }
